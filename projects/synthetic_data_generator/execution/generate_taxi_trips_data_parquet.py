from synthetic_data_generator.execution.core_engine import trip_statistics_data_parquet

size = 1000000  # Specify the number of records to generate
result = trip_statistics_data_parquet(size)
print(result)