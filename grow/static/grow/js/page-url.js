class PageUrl {
    constructor(variables = {}) {
        this.variables = variables;
    }

    setVariable(key, value) {
        this.variables[key] = value;
    }

    setVariables(variables) {
        this.variables = { ...this.variables, ...variables };
    }

    getUrl(pageUrl) {
        const url = new URL(pageUrl, window.location.origin);
        for (const [key, value] of Object.entries(this.variables)) {
            url.searchParams.set(key, value);
        }
        return url.toString();
    }

    updateUrl() {
        const url = new URL(window.location.href);
        for (const [key, value] of Object.entries(this.variables)) {
            url.searchParams.set(key, value);
        }
        window.history.replaceState({}, '', url);
    }
}
