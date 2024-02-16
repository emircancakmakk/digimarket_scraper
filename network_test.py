#!/bin/python3
import network as network

def main():
    network.dispatch_request('GET', "https://www.tme.eu/en/katalog/harting-connectors_113619/?page=1", {})

if __name__ == "__main__":
    main()
