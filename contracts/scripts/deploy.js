import { ethers } from "ethers";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function main() {
  const provider = new ethers.JsonRpcProvider("http://127.0.0.1:8545");
  // Hardhat account #0 test private key
  const testPrivKey = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80";
  const deployer = new ethers.Wallet(testPrivKey, provider);

  console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  console.log("  VeriChain Deployment Script");
  console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  console.log(`  Deployer : ${deployer.address}`);
  const balance = await provider.getBalance(deployer.address);
  console.log(`  Balance  : ${ethers.formatEther(balance)} ETH`);
  console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

  console.log("\n⏳ Deploying VeriChain contract...");

  const artifactPath = path.join(__dirname, "../artifacts/contracts/VeriChain.sol/VeriChain.json");
  const artifact = JSON.parse(fs.readFileSync(artifactPath, "utf8"));
  
  const factory = new ethers.ContractFactory(artifact.abi, artifact.bytecode, deployer);
  const verichain = await factory.deploy();
  await verichain.waitForDeployment();

  const contractAddress = await verichain.getAddress();
  console.log(`✅ VeriChain deployed to: ${contractAddress}`);

  const backendRoot = path.join(__dirname, "../../");
  const abiOutPath = path.join(backendRoot, "abi.json");
  fs.writeFileSync(abiOutPath, JSON.stringify(artifact.abi, null, 2));
  console.log(`📄 ABI written to: ${abiOutPath}`);

  const envPath = path.join(backendRoot, ".env");
  let envContent = fs.readFileSync(envPath, "utf8");

  envContent = envContent
    .replace(/^CONTRACT_ADDRESS=.*/m, `CONTRACT_ADDRESS=${contractAddress}`)
    .replace(/^RPC_URL=.*/m, `RPC_URL=http://127.0.0.1:8545`)
    .replace(/^PRIVATE_KEY=.*/m, `PRIVATE_KEY=${testPrivKey}`);

  fs.writeFileSync(envPath, envContent);
  console.log(`⚙️  .env updated`);

  console.log("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  console.log("  DEPLOYMENT COMPLETE");
  console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  console.log(`  Contract : ${contractAddress}`);
  console.log(`  RPC      : http://127.0.0.1:8545`);
  console.log(`  Deployer : ${deployer.address}`);
  console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
}

main().catch((err) => {
  console.error("❌ Deployment failed:", err.message);
  process.exit(1);
});
