"""Hosted entry point: keep each visitor's draft in their own session."""

if __name__ == "__main__":
    from workcheck.ui import main

    main(hosted=True)
