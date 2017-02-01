var runBm = runBm || { };

$(function () {

    runBm.Node = function() {
        var self = this;
        self.created_at = ko.observable();
        self.id = ko.observable();
        self.image = ko.observable();
        self.name = ko.observable();
        self.extra = ko.observable();
        self.private_ips = ko.observableArray();
        self.public_ips = ko.observableArray();
        self.size = ko.observable();
        self.state = ko.observable();
        self.uuid = ko.observable();
    };

    runBm.ParamsChoice = function() {
        var self = this;
        self.server_name = ko.observable();
        self.server_ip = ko.observable();
        self.auth_url = ko.observable();
        self.tenant = ko.observable();
        self.image = ko.observable();
        self.image_url = ko.observable();
        self.flavor = ko.observable();
        self.databases = ko.observable();
    };

    ko.bindingHandlers.loadingButton = {
        update: function(element, valueAccessor) {
            var $button, isLoading;

            $button = $(element);
            isLoading = ko.unwrap(valueAccessor());

            if (isLoading) {
                $button.button('loading');
            } else {
                $button.button('reset');
            }
        }
    };

    runBm.vm = function() {
        var
            metadata = {
                pageTitle: 'TSDBBench Web UI Login page',
                vendorlibs: [
                    'Knockout JS',
                    'JQuery',
                    'Bootstrap'
                ]
            },
            errorObj = ko.observable({
                wrongKey: ko.observable()
            }),
            benchmarkConfigs = ko.observable(),
            benchmarkIsRunning = ko.observable(),
            benchmarkDebugInfo = ko.observableArray([]),
            benchmarkResults = ko.observableArray([]),
            chosenParameters = ko.observable(),
            imagesList = ko.observable(),
            selectedImage = ko.observable(),
            flavorsList = ko.observable(),
            selectedFlavor = ko.observable(),
            databaseList = ko.observable(),
            sshEstablished = ko.observable(),
            selectedDatabase = ko.observable(),
            selectedConfiguration = ko.observable(),
            selectedDatabasesList = ko.observableArray(),
            selectedDatabasesString = ko.computed(function() {
                result = ""
                for (var s in selectedDatabasesList()) {
                    result += selectedDatabasesList()[s] + " ";
                }
                return result.trim();
            }),
            databasesToRemove = ko.observableArray(),
            nodesList = ko.observableArray(),
            selectedInstance = ko.observable(),
            checkInstanceIp = ko.computed(function() {
                if (selectedInstance()) {
                    return getNodeFloatingIp(selectedInstance().id());
                }
                else return undefined;
            }),
            selectedInstanceIp = ko.observable(),
            //selectedInstanceKeyCompatible = ko.computed(),
            initWizard = function() {
                //Initialize tooltips
                $('.nav-tabs > li a[title]').tooltip();

                //Wizard
                $('a[data-toggle="tab"]').on('show.bs.tab', function (e) {
                    var $target = $(e.target);

                    if ($target.parent().hasClass('disabled')) {
                        return false;
                    }
                });

                $(".next-step").click(function (e) {
                    var $active = $('.wizard .nav-tabs li.active');
                    $active.next().removeClass('disabled');
                    nextTab($active);
                });
                $(".prev-step").click(function (e) {
                    var $active = $('.wizard .nav-tabs li.active');
                    prevTab($active);
                });

            },
            nextTab = function(elem) {
                $(elem).next().find('a[data-toggle="tab"]').click();
            },
            prevTab = function (elem) {
                $(elem).prev().find('a[data-toggle="tab"]').click();
            },
            isKeyPairCreated = ko.observable(),
            generateKeyPair = function() {
                $.ajax({
                    type: 'POST',
                    dataType: "json",
                    url: '/genkeypair',
                    data: {},
                    success: function(data) {
                        isKeyPairCreated(data)
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
            },
            keyPairIconStyle = ko.computed(function() {
                if (isKeyPairCreated()) {
                    return {color: "green"}
                }
                else {
                    return {color: "red"}
                }
            }),
            getDatabases = function() {
                $.ajax({
                    type: "GET",
                    url: "/getdatabases",
                    data: {},
                    success: function(data) {
                        databaseList(data);
                    }
                }).fail( function( xhr, status ) {
                    if( status == "timeout" ) {
                        console.log("timeout");
                    }
                    else {
                        console.log(xhr);
                        if(status) console.log(status);
                        console.log('another error');
                    }
                });
            },
            getNodesList = function() {
                $.ajax({
                    type: 'GET',
                    dataType: "json",
                    url: '/getnodes',
                    data: {},
                    success: function(data) {
                        result = [];
                        for (var i = 0; i < data.length; i++) {
                            result.push(
                                new runBm.Node()
                                    .created_at(data[i].created_at)
                                    .id(data[i].id)
                                    .image(data[i].image)
                                    .name(data[i].name)
                                    .extra(data[i].extra)
                                    .private_ips(data[i].private_ips)
                                    .public_ips(data[i].public_ips)
                                    .size(data[i].size)
                                    .state(data[i].state)
                                    .uuid(data[i].uuid)
                            );
                        }
                        nodesList(result);
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
            },
            getNodeFloatingIp = function(node_id) {
                $.ajax({
                    type: "GET",
                    url: "/getnodefloatingip",
                    data: { node: node_id},
                    success: function(data) {
                        if (data !== 'None') {
                            selectedInstanceIp(data);
                        }
                        else {
                            selectedInstanceIp(undefined);
                        }

                    }
                }).fail( function( xhr, status ) {
                    if( status == "timeout" ) {
                        console.log("timeout");
                    }
                    else {
                        console.log(xhr);
                        if(status) console.log(status);
                        console.log('another error');
                    }
                });
            },
            addDatabase = function () {
                selectedDatabasesList.push(
                    selectedDatabase().name + '_' + selectedConfiguration()
                );
                selectedDatabase('');
            },
            removeSelectedDatabases = function () {
                selectedDatabasesList.removeAll(databasesToRemove());
                databasesToRemove([]); // Clear selection
            },
            sshExecuteBenchmark = function() {
                benchmarkIsRunning(true);
                benchmarkDebugInfo([]);
                $.ajax({
                    type: "POST",
                    url: "/sshexecute",
                    data: {
                        server_ip: chosenParameters().server_ip(),
                        databases: chosenParameters().databases(),
                        auth_url: chosenParameters().auth_url(),
                        tenant: chosenParameters().tenant(),
                        image: chosenParameters().image(),
                        image_url: chosenParameters().image_url(),
                        flavor: chosenParameters().flavor()
                    },
                    success: function(data) {
                        benchmarkResults(data);
                        benchmarkIsRunning(false);
                        clearInterval(logging);
                        /*clearInterval(partialResults);*/
                    }
                }).fail( function( xhr, status ) {
                    benchmarkIsRunning(false);
                    clearInterval(logging);
                    /*clearInterval(partialResults);*/
                    if( status == "timeout" ) {
                        console.log("timeout");
                    }
                    else {
                        console.log(xhr);
                        if(status) console.log(status);
                        console.log('another error');
                    }
                });

                var logging = setInterval(function(){
                    getSshDebugInfo(chosenParameters().server_ip());
                }, 1000);

                /*var partialResults = undefined;
                setTimeout (function() {
                    partialResults = setInterval(function(){
                        getBenchmarkResults(chosenParameters().server_ip());
                    }, 1000);
                }, 120000);*/

                // Switch to the next step
                var $active = $('.wizard .nav-tabs li.active');
                $active.next().removeClass('disabled');
                nextTab($active);

            },
            getSshDebugInfo = function(server_ip) {
                $.ajax({
                    type: "GET",
                    url: "/sshdebuglog",
                    data: {
                        server_ip: server_ip
                    },
                    success: function(data) {
                        if (data.length > benchmarkDebugInfo().length) {
                            benchmarkDebugInfo.push(data[benchmarkDebugInfo().length]);
                        }
                    }
                }).fail( function( xhr, status ) {
                    if( status == "timeout" ) {
                        console.log("timeout");
                    }
                    else {
                        console.log(xhr);
                        if(status) console.log(status);
                        console.log('another error');
                    }
                });
            },
            getBenchmarkResults = function(server_ip) {
                $.ajax({
                    type: "GET",
                    url: "/sshbenchmarkresults",
                    data: {
                        server_ip: server_ip
                    },
                    success: function(data) {
                        for (var i = 0; i < data.length; i++) {
                            if (benchmarkResults.indexOf(data[i]) < 0) {
                                benchmarkResults.push(data[i]);
                            }
                        }

                    }
                }).fail( function( xhr, status ) {
                    if( status == "timeout" ) {
                        console.log("timeout");
                    }
                    else {
                        console.log(xhr);
                        if(status) console.log(status);
                        console.log('another error');
                    }
                });
            },
            checkKeyPair = function() {
                $.ajax({
                    type: 'GET',
                    dataType: "json",
                    url: '/checkkeypair',
                    data: {},
                    success: function(data) {
                        isKeyPairCreated(data);
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
            },
            testSSH = function(server_ip) {
                if (selectedInstance().extra().key_name === isKeyPairCreated()) {
                    console.log("key is OK");
                    $.ajax({
                        type: 'POST',
                        dataType: "json",
                        url: '/testssh',
                        data: {server_ip: server_ip},
                        success: function(data) {
                            sshEstablished(data);
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

                }
                else {
                    errorObj().wrongKey("You are not allowed to connect to selected instance with your private key. Please, create another instance.");
                }

            },
            getImagesList = function() {
                $.ajax({
                    type: 'GET',
                    dataType: "json",
                    url: '/getimages',
                    data: {},
                    success: function(data) {
                        imagesList(data);
                        for (var i = 0; i < imagesList().length; i++) {
                            if (imagesList()[i].name === benchmarkConfigs()['openstack.image']) {
                                selectedImage(imagesList()[i]);
                            }
                        }
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
            },
            getFlavorsList = function() {
                $.ajax({
                    type: 'GET',
                    dataType: "json",
                    url: '/getflavors',
                    data: {},
                    success: function(data) {
                        flavorsList(data);
                        for (var i = 0; i < flavorsList().length; i++) {
                            if (flavorsList()[i].name === benchmarkConfigs()['openstack.flavor']) {
                                selectedFlavor(flavorsList()[i]);
                            }
                        }
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
            },
            getBenchmarkConfig = function() {
                $.ajax({
                    type: 'GET',
                    dataType: "json",
                    url: '/getbenchmarkconfigs',
                    data: {},
                    success: function(data) {
                        benchmarkConfigs(data);
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
            },
            saveChosenParams = function() {
                if (selectedInstance() && benchmarkConfigs()) {
                    chosenParameters(
                        new runBm.ParamsChoice()
                            .server_name(selectedInstance().name())
                            .server_ip(selectedInstanceIp())
                            .auth_url(benchmarkConfigs()['openstack_auth_url'])
                            .tenant(benchmarkConfigs()['openstack.tenant_name'])
                            .image(selectedImage().name)
                            .image_url(benchmarkConfigs()['openstack.openstack_image_url'])
                            .flavor(selectedFlavor().name)
                            .databases(selectedDatabasesString())
                    );
                }
                else {
                    chosenParameters(undefined);
                }
            };


        return {
            addDatabase: addDatabase,
            benchmarkConfigs: benchmarkConfigs,
            benchmarkIsRunning: benchmarkIsRunning,
            benchmarkDebugInfo: benchmarkDebugInfo,
            benchmarkResults: benchmarkResults,
            checkKeyPair: checkKeyPair,
            chosenParameters: chosenParameters,
            databaseList: databaseList,
            databasesToRemove: databasesToRemove,
            errorObj: errorObj,
            flavorsList: flavorsList,
            generateKeyPair: generateKeyPair,
            getBenchmarkConfig: getBenchmarkConfig,
            getDatabases: getDatabases,
            getImagesList: getImagesList,
            getFlavorsList: getFlavorsList,
            getNodesList: getNodesList,
            imagesList: imagesList,
            initWizard: initWizard,
            isKeyPairCreated: isKeyPairCreated,
            keyPairIconStyle: keyPairIconStyle,
            nodesList: nodesList,
            removeSelectedDatabases: removeSelectedDatabases,
            saveChosenParams: saveChosenParams,
            selectedConfiguration: selectedConfiguration,
            selectedDatabase: selectedDatabase,
            selectedDatabasesList: selectedDatabasesList,
            selectedDatabasesString: selectedDatabasesString,
            selectedFlavor: selectedFlavor,
            selectedImage: selectedImage,
            selectedInstance: selectedInstance,
            selectedInstanceIp: selectedInstanceIp,
            sshExecuteBenchmark: sshExecuteBenchmark,
            sshEstablished: sshEstablished,
            testSSH: testSSH
        };

    }();

    ko.applyBindings(runBm.vm);
    runBm.vm.initWizard();
    runBm.vm.getBenchmarkConfig();
    runBm.vm.checkKeyPair();
    runBm.vm.getDatabases();
    runBm.vm.getNodesList();
    runBm.vm.getImagesList();
    runBm.vm.getFlavorsList();


});