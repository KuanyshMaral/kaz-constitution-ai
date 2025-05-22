const hre = require("hardhat");

async function main() {
  const VectorStore = await hre.ethers.getContractFactory("VectorStore");
  const vectorStore = await VectorStore.deploy();

  await vectorStore.waitForDeployment(); // вместо .deployed()

  console.log(`✅ VectorStore deployed to: ${await vectorStore.getAddress()}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});