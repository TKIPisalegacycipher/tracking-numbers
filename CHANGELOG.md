# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `possible_tracking_number()` API to return all matching candidates for a tracking number
- `get_definition()` API to look up a tracking number definition by product name
- `validate` parameter on `get_tracking_number()` to allow returning invalid matches
- Luhn and Mod_37_36 checksum algorithms
- Additional information extraction (service type, country) from tracking numbers
- Checksum validator tests with diagnostic error messages
- Python 3.12, 3.13, and partial 3.14 compatibility
- Windows compatibility
- Type annotations on `spec.py` helper methods

### Changed
- `SerialNumber` and `CheckDigit` types changed from `int` to `str` (character-based)
- `ChecksumValidator` now exposes `_check_digit()` for debugging and potential future use
- Updated `tracking_number_data` submodule to latest definitions
- Modernized pre-commit configuration for current Python versions

## [0.1.8] - 2024-10-15

### Changed
- Updated UPS definitions via codegen

## [0.1.7] - 2024-09-20

### Added
- UPS service type 68

## [0.1.6] - 2024-09-15

### Changed
- Updated tracking number data to include alpha character test for CDL

## [0.1.5] - 2024-09-10

### Fixed
- Included missing tracking number data

## [0.1.4] - 2024-09-05

### Added
- UPS service type 67

## [0.1.3] - 2024-08-20

### Fixed
- Bug where USPS tracking numbers were mistaken for DHL
- Only return tracking numbers that pass validation

### Added
- Installation instructions in README
