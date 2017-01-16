var tsdbBenchUI = tsdbBenchUI || { };

$(function () {

    tsdbBenchUI.Node = function() {
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

    ko.bindingHandlers.loadingDimmer = {
        update: function(element, valueAccessor) {
            var $button, isLoading;

            $button = $(element);
            isLoading = ko.unwrap(valueAccessor());

            if (isLoading) {
                $('#pleaseWaitDialog').modal('show');
                //$button.button('loading');
            } else {
                $('#pleaseWaitDialog').modal('hide');
                //$button.button('reset');
            }
        }
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

    tsdbBenchUI.vm = function() {
        var
            metadata = {
                pageTitle: 'TSDBBench Web UI',
                vendorlibs: [
                    'Knockout JS',
                    'JQuery',
                    'Bootstrap'
                ]
            },
            errorObj = ko.observable({
                createNodeError: ko.observable(),
                terminateNodeError: ko.observable(),
                attachIpError: ko.observable()
            }),
            isLoading = ko.observable(false),
            isKeyPairCreated = ko.observable(),
            keyPairIconStyle = ko.computed(function() {
                if (isKeyPairCreated()) {
                    return {color: "green"}
                }
                else {
                    return {color: "red"}
                }
            }),
            imagesList = ko.observableArray(),
            flavorsList = ko.observableArray(),
            nodesList = ko.observableArray(),
            nodesIsLoadingArray = ko.computed(function() {
                result = {}
                for (var i = 0; i<nodesList().length; i++) {
                    result[nodesList()[i].id()] = ko.observable(false);
                }
                return result;
            }),
            secGroupsList = ko.observableArray(),
            floatingIpList = ko.observableArray(),
            unusedFloatingIpList = ko.computed(function() {
                result = [];
                for (var i = 0; i < floatingIpList().length; i++) {
                    if (!floatingIpList()[i].node_id) {
                        result.push(floatingIpList()[i]);
                    }
                }
                return result;
            }),
            instanceToTerminate = ko.observable(),
            instanceToAttachFloatingIp = ko.observable(),
            floatingIp = ko.observable(),
            getImagesList = function() {
                $.ajax({
                    type: 'GET',
                    dataType: "json",
                    url: '/getimages',
                    data: {},
                    success: function(data) {
                        imagesList(data);
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
                                new tsdbBenchUI.Node()
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
            getSecGroupsList = function() {
                $.ajax({
                    type: 'GET',
                    dataType: "json",
                    url: '/getsecuritygroups',
                    data: {},
                    success: function(data) {
                        secGroupsList(data);
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
            getFloatingIpList = function() {
                $.ajax({
                    type: 'GET',
                    dataType: "json",
                    url: '/getfloatingips',
                    data: {},
                    success: function(data) {
                        floatingIpList(data);
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
            checkKeyPair = function() {
                $.ajax({
                    type: 'GET',
                    dataType: "json",
                    url: '/checkkeypair',
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
            createInstance = function(formElement) {
                isLoading(true);
                $.ajax({
                    type: "POST",
                    url: "/createnode",
                    data: $(formElement).serialize(),
                    success: function(data) {
                        if (data.error) {
                            console.log(data);
                            errorObj().createNodeError(data);
                        }
                        else {
                            errorObj().createNodeError(undefined);
                            getNodesList();
                            $('#createInstanceModal').modal('hide');
                        }

                        isLoading(false);
                    }
                }).fail( function( xhr, status ) {
                    isLoading(false);
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
            terminateInstance = function(node_id) {
                if (node_id === instanceToTerminate()) {
                    isLoading(true);
                    instanceToTerminate(undefined);
                    $.ajax({
                    type: "POST",
                    url: "/terminatenode",
                    data: {'instance': node_id},
                    success: function(data) {
                        if (data) {

                            for (var i = 0; i < nodesList().length; i++) {

                                if (nodesList()[i].id() === node_id) {
                                    nodesList().splice(i, 1);
                                    break;
                                }
                            }
                            nodesList.valueHasMutated();
                            isLoading(false);
                            $('#terminateDialog').modal('hide');
                        }
                        else {
                            isLoading(false);
                            terminateNodeError(data);
                        }
                    }
                    }).fail( function( xhr, status ) {
                        isLoading(false);
                        if( status == "timeout" ) {
                            console.log("timeout");
                        }
                        else {
                            console.log(xhr);
                            if(status) console.log(status);
                            console.log('another error');
                        }
                    });
                }
                else {
                    console.log("different");
                }

            },
            rebootInstance = function(node_id) {
                nodesIsLoadingArray()[node_id](true);
                $.ajax({
                    type: "POST",
                    url: "/rebootnode",
                    data: {'instance': node_id},
                    success: function(data) {
                        nodesIsLoadingArray()[node_id](false);
                        if (data) {
                            console.log("Reboot was successful")
                        }
                    }
                }).fail( function( xhr, status ) {
                    nodesIsLoadingArray()[node_id](false);
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
            startInstance = function(node_id) {
                nodesIsLoadingArray()[node_id](true);
                $.ajax({
                    type: "POST",
                    url: "/startnode",
                    data: {'instance': node_id},
                    success: function(data) {
                        if (data) {
                            console.log("Instance started successfully");
                            // dirty hack to get state update
                            setTimeout(function(){
                                getNodesList();
                                nodesIsLoadingArray()[node_id](false);
                            }, 3000);
                        }
                    }
                }).fail( function( xhr, status ) {
                    nodesIsLoadingArray()[node_id](false);
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
            stopInstance = function(node_id) {
                nodesIsLoadingArray()[node_id](true);
                $.ajax({
                    type: "POST",
                    url: "/stopnode",
                    data: {'instance': node_id},
                    success: function(data) {
                        if (data) {
                            console.log("Instance stopped successfully");
                            // dirty hack to get state update, it takes time to stop the instance
                            setTimeout(function(){
                                getNodesList();
                                nodesIsLoadingArray()[node_id](false);
                            }, 15000);
                        }
                    }
                }).fail( function( xhr, status ) {
                    nodesIsLoadingArray()[node_id](false);
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
            attachFloatingIp = function(floating_ip, node_id) {
                isLoading(true);
                $.ajax({
                    type: "POST",
                    url: "/attachfloatingip",
                    data: {'instance': node_id(), 'floating_ip': floating_ip()},
                    success: function(data) {
                        isLoading(false);
                        console.log(data);
                        if (data) {
                            getNodesList();
                            console.log("Floating IP was successfully attached");
                            $('#attachFloatingIpModal').modal('hide');
                        }
                    }
                }).fail( function( xhr, status ) {
                    isLoading(false);
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
            toggleTerminateDialog = function(node_id) {
                instanceToTerminate(node_id);
                $('#terminateDialog').modal('show');
            },
            toggleFloatingIpDialog = function(node_id) {
                getFloatingIpList();
                instanceToAttachFloatingIp(node_id);
                $('#attachFloatingIpModal').modal('show');
            },
            toggleCreateInstanceDialog = function() {
                initLists();
                $('#createInstanceForm')[0].reset();
                $('#createInstanceModal').modal('show');
            },
            initLists = function() {
                checkKeyPair();
                getImagesList();
                getFlavorsList();
                getSecGroupsList();
            },
            initUI = function() {
                $('#terminateDialog').on('hidden.bs.modal', function () {
                    instanceToTerminate(undefined);
                });

                $('#attachFloatingIpModal').on('hidden.bs.modal', function () {
                    instanceToAttachFloatingIp(undefined);
                });
            };

            return {
                attachFloatingIp: attachFloatingIp,
                checkKeyPair: checkKeyPair,
                createInstance: createInstance,
                errorObj: errorObj,
                flavorsList: flavorsList,
                floatingIp: floatingIp,
                floatingIpList: floatingIpList,
                generateKeyPair: generateKeyPair,
                getFlavorsList: getFlavorsList,
                getImagesList: getImagesList,
                getNodesList: getNodesList,
                getSecGroupsList: getSecGroupsList,
                imagesList: imagesList,
                initLists: initLists,
                initUI: initUI,
                instanceToTerminate: instanceToTerminate,
                instanceToAttachFloatingIp: instanceToAttachFloatingIp,
                isKeyPairCreated: isKeyPairCreated,
                isLoading: isLoading,
                keyPairIconStyle: keyPairIconStyle,
                nodesList: nodesList,
                nodesIsLoadingArray: nodesIsLoadingArray,
                rebootInstance: rebootInstance,
                secGroupsList: secGroupsList,
                startInstance: startInstance,
                stopInstance: stopInstance,
                terminateInstance: terminateInstance,
                toggleCreateInstanceDialog: toggleCreateInstanceDialog,
                toggleFloatingIpDialog: toggleFloatingIpDialog,
                toggleTerminateDialog: toggleTerminateDialog,
                unusedFloatingIpList: unusedFloatingIpList
            };
}();

    ko.applyBindings(tsdbBenchUI.vm);
    tsdbBenchUI.vm.initUI();
    tsdbBenchUI.vm.getNodesList();
    tsdbBenchUI.vm.checkKeyPair();

});