import argparse
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument("f1")
parser.add_argument("f2")
parser.add_argument("-o", required=True, help="path to output file")
args = parser.parse_args()

df1 = pd.read_csv(args.f1, index_col="name")
df2 = pd.read_csv(args.f2, index_col="name")

df = df1.loc[df1.index.difference(df2.index)]

df.to_csv(args.o)