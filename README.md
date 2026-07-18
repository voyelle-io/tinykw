![Workflow Status](https://github.com/voyelle-io/tinykw/actions/workflows/github-actions.yml/badge.svg)

# TinyKW

TinyKW ("Tiny Keyword") is a lightweight, configurable, keyword spotting engine. 

It can be used as a Wake word, or for simple Voice commands interactions, on cortex-M MCUs, Raspberry Pi and desktops.

## Installation

Precompiled binaries and shared C header are available under [libs/](libs/) and [include/](include/) respectively.

A Python binding that closely follows the C API is also available at [python-binding](python-binding/).

## Usage

Before use, keywords must be encoded using the [web encoder](https://voyelle.io/tinykw). The encoder outputs a binary representation ready to paste directly into the C or Python code.

```C
#include "tinykw.h"

tkw_status status = tkw_init();

uint32_t kw_id;
status = tkw_add_keyword(keyword_bytes, detection_threshold, &kw_id);
// ...
status = tkw_process_frame(samples, size);
// ...
uint32_t is_detected = 0;
status = tkw_is_keyword_detected(kw_id, &is_detected);
if (is_detected)
    status = tkw_clear_keyword_flag(kw_id);
```

See [examples/C](examples/C/) and [examples/Python](examples/python/) for full examples.

## License

TinyKW is free for non-commercial use, including research, education, prototyping, and evaluation.
Please see [LICENSE](LICENSE) for details. For commercial enquiries, please contact [contact@voyelle.io](mailto:contact@voyelle.io).
