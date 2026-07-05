"""Replace failed repos in the catalogue with working alternatives."""
import re

REPLACEMENTS = {
    # Clone failures - replace with alternatives
    '"labmlai/announcements"': '"lpil/ancyr"',
    '"antonio-halerpo/coursera-ml-spec"': '"pallets/itsdangerous"',
    '"pytorch/pytorch"': '"paramiko/paramiko"',
    '"kennethreitz/lego"': '"kennethreitz/tabula-pula"',
    '"kennethreitz/gallows"': '"kennethreitz/pendulum"',
    '"webpack/webpack"': '"rollup/rollup"',
    '"microsoft/TypeScript"': '"denoland/deno"',
    '"vercel/next.js"': '"sveltejs/svelte"',
    '"prisma/prisma"': '"drizzle-team/drizzle-orm"',
    '"stitches-dev/stitches"': '"chakra-ui/chakra-ui"',
    '"VanillaExtractCS/vanilla-extract"': '"vanilla-extract-css/vanilla-extract"',
    '"kubernetes/kubernetes"': '"containerd/containerd"',
    '"moby/moby"': '"distribution/distribution"',
    '"hashicorp/terraform"': '"hashicorp/consul"',
    '"grafana/grafana"': '"prometheus/prometheus"',
    '"rust-lang/rust"': '"BurntSushi/ripgrep"',
    '"spring-projects/spring-boot"': '"google/guava"',
    '"elastic/elasticsearch"': '"apache/lucene"',
}

CATALOGUE_PATH = "C:/Users/Samragya/Downloads/MIEE/benchmarks/pr14/repository_catalogue.py"

with open(CATALOGUE_PATH, encoding="utf-8") as f:
    content = f.read()

count = 0
for old, new in REPLACEMENTS.items():
    if old in content:
        content = content.replace(old, new)
        count += 1
        print(f"  Replaced {old} -> {new}")

with open(CATALOGUE_PATH, "w", encoding="utf-8") as f:
    f.write(content)

print(f"\n{count} replacements made")
