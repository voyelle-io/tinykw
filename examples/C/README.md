## Pre-requisites

[Portaudio](https://portaudio.com/) is required for reading the microphone.

The Makefile should also be adapted based on the build platform.

## Usage

```bash
make
```

```bash
./build/microphone_portaudio.bin
```

Adding the path to the dynamic library might be necessary before running the executable.
On Mac Intel, this can be done by running the command
`export DYLD_LIBRARY_PATH=../../libs/macos-x86_64/en:$DYLD_LIBRARY_PATH`.
On Linux, `export LD_LIBRARY_PATH=../../libs/linux-x86_64/en:$LD_LIBRARY_PATH`.