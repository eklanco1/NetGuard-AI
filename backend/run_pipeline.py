
from pipeline.load import load_data
from pipeline.transform import transform_data


def run_pipeline():

    print("Pokretanje NetGuard AI pipelinea...")

    print("\n1. EXTRACT + LOAD")
    load_data()

    print("\n2. TRANSFORM")
    transform_data()

    print("\nELT pipeline uspjesno zavrsen!")


if __name__ == "__main__":
    run_pipeline()
