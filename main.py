from utils.clustering import (
    process_year,
    run_all_years,
)
from utils.data_loading import (
    AVAILABLE_YEARS,
)


def main() -> None:
    """Runs the interactive pipeline entry point.

    Prompts for a specific year (2015-2023) or the word "all" and
    routes execution to the corresponding processor.
    """

    user_input = input("Enter the year for analysis (2015-2023) or 'all': ").strip().lower()

    if user_input == "all":
        run_all_years()
    else:
        try:
            chosen_year = int(user_input)
            if chosen_year not in AVAILABLE_YEARS:
                raise ValueError
            process_year(chosen_year)
        except ValueError:
            print("Invalid input. Enter a year between 2015 and 2023 or 'all'.")


if __name__ == "__main__":
    main()
