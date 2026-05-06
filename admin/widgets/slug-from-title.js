const IdTechControl = createClass({
    getInitialState() {
        return {
            touched: !!this.props.value,
        };
    },

    slugify(text) {
        return (text || "")
            .toString()
            .toLowerCase()
            .trim()
            .replace(/\s+/g, "-")
            .replace(/[^\w-]+/g, "")
            .replace(/--+/g, "-");
    },

    getEnglishTitle(props) {
        if (!props.entry) return "";

        return (
            props.entry.getIn(["i18n", "en", "data", "title"]) ||
            ""
        );
    },

    updateFromEnglishTitle(props) {
        if (this.state.touched || props.value) return;

        const englishTitle = this.getEnglishTitle(props);

        if (englishTitle) {
            props.onChange(this.slugify(englishTitle));
        }
    },

    componentDidMount() {
        this.updateFromEnglishTitle(this.props);
    },

    componentDidUpdate(prevProps) {
        const oldTitle = this.getEnglishTitle(prevProps);
        const newTitle = this.getEnglishTitle(this.props);

        if (newTitle && newTitle !== oldTitle) {
            this.updateFromEnglishTitle(this.props);
        }
    },

    render() {
        const englishTitle = this.getEnglishTitle(this.props);

        return h("div", {}, [
            h("input", {
                type: "text",
                value: this.props.value || "",
                placeholder: "Wird automatisch aus dem EN Titel erzeugt.",
                onChange: (e) => {
                    this.setState({ touched: true });
                    this.props.onChange(e.target.value);
                },
                style: {
                    width: "100%",
                    padding: "16px 20px",
                    border: "2px solid #dfdfe3",
                    borderRadius: "4px",
                    fontSize: "15px",
                },
            }),

            !englishTitle &&
            h(
                "p",
                {
                    style: {
                        marginTop: "8px",
                        color: "#b00020",
                        fontSize: "13px",
                    },
                },
                "Bitte zuerst den englischen Titel ausfüllen."
            ),
        ]);
    },
});

CMS.registerWidget("id_tech_auto", IdTechControl);