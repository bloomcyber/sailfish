# Copyright(C) Facebook, Inc. and its affiliates.
from os.path import join

from benchmark.utils import PathMaker


class CommandMaker:

    @staticmethod
    def cleanup():
        return (
            f'rm -r .db-* ; rm .*.json ; mkdir -p {PathMaker.results_path()}'
        )

    @staticmethod
    def clean_logs():
        return f'rm -r {PathMaker.logs_path()} ; mkdir -p {PathMaker.logs_path()}'

    @staticmethod
    def compile():
        return 'cargo build --quiet --release --features benchmark'

    @staticmethod
    def generate_key(filename):
        assert isinstance(filename, str)
        return f'./node generate_keys --filename {filename}'

    @staticmethod
    def run_primary(keys, committee, store, parameters, debug=False):
        assert isinstance(keys, str)
        assert isinstance(committee, str)
        assert isinstance(parameters, str)
        assert isinstance(debug, bool)
        v = '-vvv' if debug else '-vv'
        return (f'./node {v} run --keys {keys} --committee {committee} '
                f'--store {store} --parameters {parameters} primary')

    @staticmethod
    def run_worker(keys, committee, store, parameters, id, debug=False):
        assert isinstance(keys, str)
        assert isinstance(committee, str)
        assert isinstance(parameters, str)
        assert isinstance(debug, bool)
        v = '-vvv' if debug else '-vv'
        return (f'./node {v} run --keys {keys} --committee {committee} '
                f'--store {store} --parameters {parameters} worker --id {id}')

    @staticmethod
    def run_client(address, size, burst, rate, nodes):
        assert isinstance(address, str)
        assert isinstance(size, int) and size > 0
        assert isinstance(burst, int) and burst > 0
        assert isinstance(rate, int) and rate >= 0
        assert isinstance(nodes, list)
        assert all(isinstance(x, str) for x in nodes)
        nodes = f'--nodes {" ".join(nodes)}' if nodes else ''
        return f'./benchmark_client {address} --size {size} --burst {burst} --rate {rate} {nodes}'

    @staticmethod
    def run_worker_rpc_client(endpoint, size, burst, rate, nodes, jwt, mnemonic, txs):
        assert isinstance(endpoint, str)
        assert isinstance(size, int) and size > 0
        assert isinstance(burst, int) and burst > 0
        assert isinstance(rate, int) and rate >= 0
        assert isinstance(nodes, list)
        assert all(isinstance(x, str) for x in nodes)
        assert isinstance(jwt, str)
        assert isinstance(mnemonic, str)
        assert isinstance(txs, int) and txs > 0
        nodes = f'--nodes {" ".join(nodes)}' if nodes else ''
        return (
            f'./worker_rpc_client {endpoint} --size {size} --burst {burst} '
            f'--rate {rate} {nodes} --jwt-secret {jwt} --mnemonic {mnemonic} '
            f'--transactions {txs}'
        )

    @staticmethod
    def kill():
        return 'tmux kill-server'

    @staticmethod
    def alias_binaries(origin):
        assert isinstance(origin, str)
        node = join(origin, 'node')
        client = join(origin, 'benchmark_client')
        rpc_client = join(origin, 'worker_rpc_client')
        return (
            f'rm node ; rm benchmark_client ; rm worker_rpc_client ; '
            f'ln -s {node} . ; ln -s {client} . ; ln -s {rpc_client} .'
        )
