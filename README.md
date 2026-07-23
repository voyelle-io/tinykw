![Workflow Status](https://github.com/voyelle-io/tinykw/actions/workflows/github-actions.yml/badge.svg)

# TinyKW

TinyKW ("Tiny Keyword") is a lightweight, configurable, keyword spotting engine. 

It can be used for Wake word detection and simple Voice commands, on cortex-M MCUs, Raspberry Pi and desktops.

## Installation

Precompiled binaries and headers are available under [libs/](libs/).

A Python binding that closely follows the C API is also available at [python-binding](python-binding/).

## Usage

Before use, keywords must be encoded using the [web encoder](https://voyelle.io/tinykw). The encoder outputs a binary representation ready to paste directly into the C or Python code.

```C
#include "tinykw.h"

tkw_context ctx;
tkw_status status = tkw_init(&ctx);

uint32_t kw_id;
status = tkw_add_keyword(keyword_bytes, detection_threshold, &kw_id, &ctx);
// ...
status = tkw_process_frame(samples, size, &ctx);
// ...
uint32_t is_detected = 0;
status = tkw_is_keyword_detected(kw_id, &is_detected, &ctx);
if (is_detected)
    status = tkw_clear_keyword_flag(kw_id, &ctx);
```

See [examples/C](examples/C/) and [examples/Python](examples/python/) for full examples.

## License

TinyKW is free for non-commercial use, including research, education, prototyping, and evaluation.
Please see [LICENSE](LICENSE) for details. For commercial enquiries, please contact [contact@voyelle.io](mailto:contact@voyelle.io).
