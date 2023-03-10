import argparse
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument("filename")
parser.add_argument("-o", help="path to output file. If not specified, the input file is updated in-place")
args = parser.parse_args()

# Read the CSV file into a pandas DataFrame
df = pd.read_csv(args.filename)

# Drop duplicates
df = df.drop_duplicates(
    subset=["name"]
).sort_values(
    by='name', ascending=True, key=lambda k: k.str.lower()
)

# Write the de-duplicated DataFrame to a new CSV file
if args.o is not None:
    df.to_csv(args.o, index=False)
else:
    df.to_csv(args.filename, index=False)