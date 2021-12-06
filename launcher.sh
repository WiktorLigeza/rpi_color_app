#!bin/bash
cd ${0%/*}
arch=$(uname -m)
if [[ $arch == armv7l* ]]; then
  ./dist/main --run
else
    echo "This binary file supports armv7l architecture, you are using: $(arch)."
    echo "Get proper application realise from: https://drive.google.com/drive/folders/14EcpuUruE-guHCNSY5CdI2Mm2AD1yPBK?usp=sharing"
fi