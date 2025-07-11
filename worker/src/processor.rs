// Copyright(C) Facebook, Inc. and its affiliates.
use crate::worker::SerializedBatchDigestMessage;
use config::WorkerId;
use crypto::Digest;
use ed25519_dalek::Digest as _;
use ed25519_dalek::Sha512;
use hex;
use primary::WorkerPrimaryMessage;
use log::{debug, error, info};
use std::convert::TryInto;
use store::Store;
use tokio::sync::mpsc::{Receiver, Sender};

#[cfg(test)]
#[path = "tests/processor_tests.rs"]
pub mod processor_tests;

/// Indicates a serialized `WorkerMessage::Batch` message.
pub type SerializedBatchMessage = Vec<u8>;

/// Hashes and stores batches, it then outputs the batch's digest.
pub struct Processor;

impl Processor {
    pub fn spawn(
        // Our worker's id.
        id: WorkerId,
        // The persistent storage.
        mut store: Store,
        // Input channel to receive batches.
        mut rx_batch: Receiver<SerializedBatchMessage>,
        // Output channel to send out batches' digests.
        tx_digest: Sender<SerializedBatchDigestMessage>,
        // Whether we are processing our own batches or the batches of other nodes.
        own_digest: bool,
    ) {
        tokio::spawn(async move {
            while let Some(batch) = rx_batch.recv().await {
                // Hash the batch.
                let digest = Digest(Sha512::digest(&batch).as_slice()[..32].try_into().unwrap());
                debug!("Hashed batch to digest {}", digest);

                // Try to deserialize the batch to log its transactions.
                match bincode::deserialize::<crate::worker::WorkerMessage>(&batch) {
                    Ok(crate::worker::WorkerMessage::Batch(txs)) => {
                        let tx_strings: Vec<String> = txs.iter().map(|t| hex::encode(t)).collect();
                        info!("Batch {} contains txs {:?}", digest, tx_strings);
                    }
                    Ok(_) => {
                        // Unexpected worker message variant.
                        error!("Unexpected worker message for batch {}", digest);
                    }
                    Err(e) => {
                        error!("Failed to deserialize batch {}: {}", digest, e);
                    }
                }

                // Store the batch.
                store.write(digest.to_vec(), batch).await;
                debug!("Stored batch {}", digest);

                // Deliver the batch's digest.
                let message = match own_digest {
                    true => WorkerPrimaryMessage::OurBatch(digest, id),
                    false => WorkerPrimaryMessage::OthersBatch(digest, id),
                };
                let message = bincode::serialize(&message)
                    .expect("Failed to serialize our own worker-primary message");
                tx_digest
                    .send(message)
                    .await
                    .expect("Failed to send digest");
            }
        });
    }
}
