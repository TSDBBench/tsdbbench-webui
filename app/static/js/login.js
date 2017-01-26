var loginUI = loginUI || { };

$(function () {

    loginUI.Provider = function(name) {
        var self = this;
        this
        this.countryName = name;
        this.countryPopulation = population;
    };

    loginUI.vm = function() {
        var
            metadata = {
                pageTitle: 'TSDBBench Web UI Login page',
                vendorlibs: [
                    'Knockout JS',
                    'JQuery',
                    'Bootstrap'
                ]
            },
            selectedProvider = ko.observable(),
            selectedProviderFields = ko.computed(function() {
                result = [];
                for (var key in selectedProvider()) {
                    if (selectedProvider().hasOwnProperty(key) && key !== 'provider') {
                        var obj = {
                            'name': key,
                            'nameCap': key.charAt(0).toUpperCase() + key.slice(1),
                            'value': selectedProvider()[key]
                        };
                        result.push(obj);
                    }
                }

                return result;
            }),
            providersConfigs = ko.observableArray(),

            getProvidersSettings = function() {
                $.ajax({
                    type: 'GET',
                    dataType: "json",
                    url: '/getprovidersettings',
                    data: {},
                    success: function(data) {
                        providersConfigs(data);
                    },
                    timeout: 5000
                }).fail( function( xhr, status ) {
                    if( status == "timeout" ) {
                        console.log('timeout');
                    }
                    else {
                        console.log(xhr);
                        if(status) console.log(status);
                        console.log('another error');
                    }
                });
            };


        return {
            selectedProvider: selectedProvider,
            selectedProviderFields: selectedProviderFields,
            providersConfigs: providersConfigs,
            getProvidersSettings: getProvidersSettings
        };

    }();

    ko.applyBindings(loginUI.vm);
    loginUI.vm.getProvidersSettings();

});