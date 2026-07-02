import process from "node:process";

const runtimeContext = {
  node: process.version,
  platform: process.platform,
  arch: process.arch,
  npm_config_user_agent: process.env.npm_config_user_agent ?? "unknown",
  vitest_pool: process.env.VITEST_POOL ?? "default",
};

console.log("[smoke] frontend runtime context");
for (const [key, value] of Object.entries(runtimeContext)) {
  console.log(`[smoke] ${key}: ${value}`);
}
