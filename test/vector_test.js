const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("VectorStore", function () {
  let vectorStore;

  beforeEach(async () => {
    const VectorStore = await ethers.getContractFactory("VectorStore");
    vectorStore = await VectorStore.deploy();
    await vectorStore.deployed();
  });

  it("should store and retrieve a vector", async function () {
    const id = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("vec1"));
    const values = [1, 2, 3, 4];
    await vectorStore.storeVector(id, values);
    const stored = await vectorStore.getVector(id);
    expect(stored.map(v => Number(v))).to.eql(values);
  });

  it("should update an existing vector", async function () {
    const id = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("vec2"));
    await vectorStore.storeVector(id, [1, 1, 1]);
    await vectorStore.updateVector(id, [9, 9, 9]);
    const updated = await vectorStore.getVector(id);
    expect(updated.map(v => Number(v))).to.eql([9, 9, 9]);
  });

  it("should not store duplicate vector", async function () {
    const id = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("vec3"));
    await vectorStore.storeVector(id, [1]);
    await expect(vectorStore.storeVector(id, [2])).to.be.revertedWith("Vector already exists");
  });
});