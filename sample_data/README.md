# Synthetic Power BI test data

`pulse_test_data.csv` contains fictional, deterministic data for validating PULSE without using business data. It has 24 transactions across six months, four regions, three categories, and three products.

## Import and model

Import the CSV into a Power BI semantic model and name the table `PulseTestData`. Confirm these data types:

| Column | Type |
|---|---|
| `TransactionID` | Text |
| `Date` | Date |
| `Region`, `Category`, `Product` | Text |
| `Units` | Whole number |
| `UnitPrice`, `Revenue` | Decimal or fixed decimal number |
| `QualityStatus`, `PartialNote`, `AlwaysBlank` | Text |

`AlwaysBlank` is intentionally empty in every row. `PartialNote` contains a mixture of populated and empty values and acts as a negative control: it must not be classified as an entirely blank column.

The expected base totals are:

- 122 units
- 15,510 revenue
- 24 transactions
- 5 rows with `QualityStatus = "Warning"`

## Measures

Create these measures:

```DAX
Total Revenue =
SUM(PulseTestData[Revenue])
```

```DAX
Total Units =
SUM(PulseTestData[Units])
```

```DAX
Transaction Count =
COUNTROWS(PulseTestData)
```

```DAX
Warning Count =
CALCULATE(
    COUNTROWS(PulseTestData),
    PulseTestData[QualityStatus] = "Warning"
)
```

```DAX
Always Blank Measure =
BLANK()
```

```DAX
Synthetic Error =
ERROR("Synthetic PULSE test error")
```

`Synthetic Error` is intentional and must only be used in the disposable test report.

## Suggested report

Name the report `PULSE Synthetic Test` and enable every visual title exactly as listed.

### Page `01 Healthy`

- `Healthy Table`: `Date`, `Region`, `Category`, `Revenue`
- `Healthy Chart`: `Date` on the axis and `Total Revenue` as the value
- `Category Slicer`: `Category`
- Cards for `Total Revenue`, `Total Units`, and `Transaction Count`

Expected behavior: supported visuals export successfully. The slicer is excluded from blank checking.

### Page `02 Blank Data`

- `Blank Column Table`: `Category`, `Total Revenue`, and `Always Blank Measure`
- `Partial Blank Control`: `TransactionID`, `Revenue`, and `PartialNote`
- `No Rows Table`: `TransactionID` and `Revenue`, with a visual-level filter of `Revenue > 5000`

Expected behavior:

- `Blank Column Table` should produce an all-blank warning.
- `Partial Blank Control` should not produce a blank-column warning because some notes are populated.
- `No Rows Table` should exercise the no-data path. Power BI may return an empty export or an export error; record which behavior occurs.

### Page `03 Error`

- `Synthetic Error Table`: `Category` and `Synthetic Error`

Expected behavior: visual evaluation/export fails and PULSE records an error.

### Page `04 Skip`

- `Configured Skip Table`: `Category` and `Total Revenue`

Use this local `.env` rule:

```dotenv
PULSE_SKIP_VISUALS_JSON=[{"report":"PULSE Synthetic Test","page":"04 Skip","visual":"Configured Skip Table"}]
```

Expected behavior: the visual appears in the `Skipped_Visuals` workbook sheet.

### Page `05 Unsupported`

Add a textbox, image, shape, and button.

Expected behavior: PULSE logs their unsupported export types, skips them, and continues.

## Deterministic slow-export test

For the first run, temporarily use very low thresholds so ordinary successful exports exercise the slow-export and Excel-highlighting branches:

```dotenv
PULSE_SLOW_EXPORT_THRESHOLD_SECONDS=0.001
PULSE_HIGHLIGHT_THRESHOLD_SECONDS=0.002
```

Restart the notebook kernel after editing `.env`. Restore the normal `2.0` and `5.0` thresholds for the subsequent realistic-duration run.
