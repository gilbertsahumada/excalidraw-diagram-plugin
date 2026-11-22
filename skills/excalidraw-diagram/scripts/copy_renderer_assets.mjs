import { cpSync, mkdirSync, rmSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const skillDir = resolve(scriptDir, "..");
const source = resolve(
  skillDir,
  "../..",
  "node_modules/@excalidraw/excalidraw/dist/prod/fonts",
);
const destination = join(skillDir, "assets/excalidraw-assets");
const keep = [
  ["Cascadia", "CascadiaCode-Regular.woff2"],
  ["Virgil", "Virgil-Regular.woff2"],
  ["Liberation", "LiberationSans-Regular.woff2"],
];

rmSync(destination, { recursive: true, force: true });
for (const [family, file] of keep) {
  mkdirSync(join(destination, family), { recursive: true });
  cpSync(join(source, family, file), join(destination, family, file));
}
