// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract VectorStore {
    struct Vector {
        int256[] values;
        bool exists;
    }

    mapping(bytes32 => Vector) private vectors;

    event VectorStored(bytes32 indexed id);
    event VectorUpdated(bytes32 indexed id);

    function storeVector(bytes32 id, int256[] memory values) public {
        require(!vectors[id].exists, "Vector already exists");
        vectors[id] = Vector(values, true);
        emit VectorStored(id);
    }

    function updateVector(bytes32 id, int256[] memory values) public {
        require(vectors[id].exists, "Vector does not exist");
        vectors[id].values = values;
        emit VectorUpdated(id);
    }

    function getVector(bytes32 id) public view returns (int256[] memory) {
        require(vectors[id].exists, "Vector does not exist");
        return vectors[id].values;
    }

    function vectorExists(bytes32 id) public view returns (bool) {
        return vectors[id].exists;
    }
}