Python binding for TinyKW.

## Installation

`pip install tinykw`

## Usage

```python
import tinykw

tinykw.tkw_init()

kw_id = tinykw.tkw_add_keyword(keyword_bytes, detection_threshold)
# ... 
tinykw.tkw_process_frame(samples)
# ...
if tinykw.tkw_is_keyword_detected(kw_id):
    tinykw.tkw_clear_keyword_flag(kw_id)
```

See [examples/python](https://github.com/voyelle-io/tinykw/tree/main/examples/python) for full usage.

## License

TinyKW is free for non-commercial use, including research, education, prototyping, and evaluation.
Please see [LICENSE](https://github.com/voyelle-io/tinykw/tree/main/LICENSE) for details. For commercial enquiries, please contact [contact@voyelle.io](mailto:contact@voyelle.io).
