# Release readiness checklist

This checklist keeps the project ready for a public-facing handoff without widening scope.

## Packaging

- Confirm the package metadata in `pyproject.toml` is correct.
- Run `python -m pip install -e .` from a clean environment.
- Validate `breaklab --help` and the main smoke commands.
- Verify the README quickstart still works exactly as written.
- Build the distribution package locally:

```bash
python -m pip install --upgrade build
python -m build
```

- Confirm the wheel and source tarball are created under the `dist/` directory.

## Versioning

- Tag the release as `v0.1.0` once the repo is green.
- Update any changelog or release notes before the tag is published.
- Keep the version number in sync with the package metadata.
- Create the tag and push it:

```bash
git tag v0.1.0
git push origin v0.1.0
```

## Public handoff

- Confirm the project is permissioned for the target being tested.
- Keep attestation strings explicit and auditable in every config.
- Save a clean sample run under `artifacts/` and a client-ready report under `examples/`.
- Share the README and the diff example as the default onboarding path.
- Publish a GitHub release with the generated package artifacts and a short summary of the verified smoke path.

## Operational notes

- Keep mock and local Python targets as the CI baseline.
- Treat external live-app runs as optional validation rather than the default test path.
- Record any non-deterministic findings separately from deterministic verdicts.

## Done when

- The local install works with no extra setup beyond the README.
- CI passes on the default regression path.
- A user can run the harness locally against a controlled target and generate a report in under 10 minutes.
