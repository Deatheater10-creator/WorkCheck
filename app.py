if __name__ == "__main__":
    # Windows maths workers re-import this file as __mp_main__. They need
    # their calculation target, not another copy of the Streamlit interface.
    from workcheck.ui import main

    main()
