"""
Download from W&B the raw dataset and apply some basic data cleaning, exporting the result to a new artifact
"""
import argparse
import logging
import pandas as pd
import wandb


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    # particular version of the artifact

    artifact_local_path = run.use_artifact(args.input_artifact).file()
    logger.info(f'Download artifact: {args.input_artifact}')

    df = pd.read_csv(artifact_local_path)

    logger.info('Remove outliers. Min and max values are {args.min_price} and {args.max_price}')
    min_price = args.min_price
    max_price = args.max_price
    idx = df["price"].between(args.min_price, max_price)
    df = df[idx].copy()

    idx = df['longitude'].between(-74.25, -73.50) & df['latitude'].between(40.5, 41.2)
    df = df[idx].copy()

    logger.info('Save cleaned data.')
    df.to_csv(args.output_artifact, index=False)

    artifact = wandb.Artifact(
        args.output_artifact,
        type=args.output_type,
        description=args.output_description
    )

    artifact.add_file(args.output_artifact)
    run.log_artifact(artifact)

    artifact.wait()
    logger.info('Uploaded cleaned data.')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A very basic data cleaning")

    parser.add_argument(
        "--input_artifact", 
        type=str,
        help='Name of uncleaned dataset.',
        required=True
    )

    parser.add_argument(
        "--output_artifact", 
        type=str,
        help='Name of cleaned dataset.',
        required=True
    )

    parser.add_argument(
        "--output_type", 
        type=str,
        help='Type of output.',
        required=True
    )

    parser.add_argument(
        "--output_description", 
        type=str,
        help='Description of output dataset.',
        required=True
    )

    parser.add_argument(
        "--min_price", 
        type=float,
        help='Minimum price. Lower values are outliers and will be removed.',
        required=True
    )

    parser.add_argument(
        "--max_price", 
        type=float,
        help='Maximum price. Higher values are outliers and will be removed.',
        required=True
    )


    args = parser.parse_args()

    go(args)
