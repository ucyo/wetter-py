# Data

The [measurement data](./data.json) is stored in this folder.
Further, the folder also contains a [test dataset](./test.json) being used for `pytest` runs.
The data is a serialized `pandas.DataFrame` which is saved using the following
settings:

```python
df.T.to_json(db_location, orient="split", date_format="iso")
```

The `pandas.DataFrame` is first transposed `T` and then `split`. This setup uses less storage
space since the labels are only used once and the data is saved consecutively.
Further, the `date_format` changes the output to use a standardized `iso` format.
It has the advantage that time zone information is also added into the output.
