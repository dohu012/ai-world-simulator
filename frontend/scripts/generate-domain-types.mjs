import { mkdir, readdir, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

import { compileFromFile } from "json-schema-to-typescript";
import { format } from "prettier";

const frontendDirectory = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  "..",
);
const schemaDirectory = path.resolve(
  frontendDirectory,
  "..",
  "schemas",
  "domain",
);
const outputDirectory = path.resolve(
  frontendDirectory,
  "src",
  "types",
  "generated",
);

const schemaFiles = (await readdir(schemaDirectory))
  .filter((filename) => filename.endsWith(".schema.json"))
  .sort();

await mkdir(outputDirectory, { recursive: true });

for (const schemaFile of schemaFiles) {
  const outputFile = schemaFile.replace(/\.json$/, ".d.ts");
  const declaration = await compileFromFile(
    path.join(schemaDirectory, schemaFile),
    {
      additionalProperties: false,
      bannerComment:
        "/* eslint-disable */\n" +
        "/** Generated from schemas/domain. Do not edit by hand. */",
      unknownAny: true,
    },
  );
  const formattedDeclaration = await format(declaration, {
    parser: "typescript",
  });
  await writeFile(
    path.join(outputDirectory, outputFile),
    formattedDeclaration.replaceAll("\r\n", "\n"),
    "utf8",
  );
}
