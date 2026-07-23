# Python binding for TinyKW

## Installation

```
pip install tinykw
```

## Usage

```python
from tinykw import TkwEngine

engine = TkwEngine(language="es")

kw_id = engine.add_keyword(data=kw_bytes, detection_threshold=0.5)
# ... 
engine.process_frame(samples)
# ...
if engine.is_keyword_detected(kw_id):
    engine.clear_keyword_flag(kw_id)
```

See [examples/python](https://github.com/voyelle-io/tinykw/tree/main/examples/python) for full usage.

## License

TinyKW is free for non-commercial use, including research, education, prototyping, and evaluation.
Please see [LICENSE](https://github.com/voyelle-io/tinykw/tree/main/LICENSE) for details. For commercial enquiries, please contact [contact@voyelle.io](mailto:contact@voyelle.io).
