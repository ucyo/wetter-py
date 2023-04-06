# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> Hint: Added, Changed, Fixed, Removed, Updated.

## [Unreleased]

## [v0.3.1] - 2023-04-04

### Added
- MIT license
- CLI subcommand `compare --month X` as `compare-details` alternative
- CLI subcommand `config` for printing configuration and systemd/cron setup
- Configuration module
- Definition of the serialization structure for backend
- Parser for serialization structure via custom `json.JSONEncoder`
- API for Historical Data from OpenMeteo Archive

### Fixed
- Bug in `compared-details` method

### Removed
- Testdata from the package
- CLI subcommand `compare-details`

### Updated
- Documentation for the package
- Tests for the backend system
- Tests for the configuration management

## [v0.3.0] - 2023-04-03

### Added
- MVP of the main tasks for comparison and latest measurement as well as update

### Changed
- Restructuring of the code backend

## [v0.2.0-rc.1] - 2023-04-03

### Added
- CI/CD workflow for release creation
- CI/CD workflow for static analysis
- CI/CD workflow for build, install and test
- Test data from OpenMeteo
- Scaffolding for CLI tool
- Setup of Dockerfile and Makefile
