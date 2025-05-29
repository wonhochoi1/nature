#!/bin/bash
set -e

# Ensure we're in the right environment if conda is being used
if command -v conda &> /dev/null && [[ "$CONDA_DEFAULT_ENV" != "nature-env" && -d "$CONDA_PREFIX/envs/nature-env" ]]; then
    echo "Note: It's recommended to activate the nature-env conda environment:"
    echo "conda activate nature-env"
fi

echo "Cleaning previous build..."
cargo clean

echo "Building nature in release mode..."
cargo build --release

# Check if build was successful
if [ ! -f "target/release/nature" ]; then
    echo "Build failed!"
    exit 1
fi

echo "Making nature script executable..."
chmod +x nature

echo "Build successful!"
echo "You can now run your nature programs with:"
echo "./nature examples/demo.nature" 