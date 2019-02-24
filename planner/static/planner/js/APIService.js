class APIService {
    constructor(base, csrf){
        this.base = base;
        this.headers = { 'X-CSRFToken': csrf }
    }

    url(pk) {
        let url = this.base;
        if (pk != null) {
            url = url + pk + '/'
        }
        return url;
    }

    list() {
        return axios.get(this.base).then(response => response.data.results);
    }

    retrieve(pk) {
        return axios.get(this.url(pk)).then(response => response.data);
    }

    create(team){
        return axios.post(this.base,team,{headers: this.headers});
    }

    update(pk, team){
        return axios.put(this.url(pk),team,{headers: this.headers});
    }
    
    remove(pk){
        return axios.delete(this.url(pk),{headers: this.headers});
    }
}
