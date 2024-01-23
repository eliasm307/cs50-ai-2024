import csv
import sys
from typing import List, Literal, Tuple, TypedDict
from numpy import array

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


class RawDataRow(TypedDict):
    Administrative: str  # int
    Administrative_Duration: str  # int
    Informational: str  # int
    Informational_Duration: str  # int
    ProductRelated: str  # int
    ProductRelated_Duration: str  # int
    BounceRates: str  # int
    ExitRates: str  # int
    PageValues: str  # int
    SpecialDay: str  # int
    """
    From 0 (January) to 11 (December)
    """
    Month: str  # Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    OperatingSystems: str  # int
    Browser: str  # int
    Region: str  # int
    TrafficType: str  # int
    """
    0 (not returning) or 1 (returning)
    """
    VisitorType: str  # Literal[0, 1]
    """
    int 0 (if false) or 1 (if true)
    """
    Weekend: str  # Literal[0, 1]
    Revenue: str  # Literal[0, 1]


EvidenceRow = Tuple[
    int,  # Administrative
    float,  # Administrative_Duration
    int,  # Informational
    float,  # Informational_Duration
    int,  # ProductRelated
    float,  # ProductRelated_Duration
    float,  # BounceRates
    float,  # ExitRates
    float,  # PageValues
    float,  # SpecialDay
    int,  # Month (0-11)
    int,  # OperatingSystems
    int,  # Browser
    int,  # Region
    int,  # TrafficType
    int,  # VisitorType (0 or 1)
    int,  # Weekend (0 or 1)
]

Label = Literal[0, 1]


def main():
    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    print("evidence rows:", len(evidence), "; labels rows", len(labels))
    print("evidence columns:", len(evidence[0]))
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)  # type: ignore

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename: str) -> tuple[list[EvidenceRow], list[Label]]:
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """

    MONTH_TO_INT_MAP = {
        "Jan": 0,
        "Feb": 1,
        "Mar": 2,
        "Apr": 3,
        "May": 4,
        "June": 5,
        "Jul": 6,
        "Aug": 7,
        "Sep": 8,
        "Oct": 9,
        "Nov": 10,
        "Dec": 11,
    }

    # VisitorType should be 1 for returning visitors and 0 for non-returning visitors.
    VISITOR_TYPE_TO_INT_MAP = {
        "New_Visitor": 0,
        "Returning_Visitor": 1,
        "Other": 0,
    }

    evidence: List[EvidenceRow] = []
    labels: List[Label] = []

    with open(filename) as file:
        for _row in csv.DictReader(file):
            row: RawDataRow = _row  # type: ignore
            evidence.append(
                (
                    int(row["Administrative"]),
                    float(row["Administrative_Duration"]),
                    int(row["Informational"]),
                    float(row["Informational_Duration"]),
                    int(row["ProductRelated"]),
                    float(row["ProductRelated_Duration"]),
                    float(row["BounceRates"]),
                    float(row["ExitRates"]),
                    float(row["PageValues"]),
                    float(row["SpecialDay"]),
                    MONTH_TO_INT_MAP[row["Month"]],
                    int(row["OperatingSystems"]),
                    int(row["Browser"]),
                    int(row["Region"]),
                    int(row["TrafficType"]),
                    VISITOR_TYPE_TO_INT_MAP[row["VisitorType"]],
                    parse_bool_to_int(row["Weekend"]),
                )
            )

            labels.append(parse_bool_to_int(row["Revenue"]))

    return (evidence, labels)


def parse_bool_to_int(value: str) -> Literal[0, 1]:
    return 1 if value == "TRUE" else 0


def train_model(evidence: list[EvidenceRow], labels: list[Label]):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    model = KNeighborsClassifier(n_neighbors=1)
    model.fit(array(evidence), labels)
    return model


def evaluate(labels: list[Label], predictions: list[Label]) -> tuple[float, float]:
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificity).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """

    expected_positive_count = 0
    expected_negative_count = 0
    correctly_predicted_positive_count = 0
    correctly_predicted_negative_count = 0
    # NOTE: we need to compare labels by index so we can correlate accuracy properly,
    # we should not just count the overall positive/negative predictions and compare those to the positive/negative labels
    for label, prediction in zip(labels, predictions, strict=True):
        if label == 0:  # expected negative
            expected_negative_count += 1
            if label == prediction:
                correctly_predicted_negative_count += 1

        else:  # expected positive
            expected_positive_count += 1
            if label == prediction:
                correctly_predicted_positive_count += 1

    # return (sensitivity, specificity)
    return (
        correctly_predicted_positive_count / expected_positive_count,
        correctly_predicted_negative_count / expected_negative_count,
    )


if __name__ == "__main__":
    main()
