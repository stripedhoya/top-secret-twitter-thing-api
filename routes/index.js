var express = require('express');
var router = express.Router();

var redis = require("redis"), client = redis.createClient();

client.on("error", function (err) {
    console.log("Error " + err);
});

var livingDB = {};

var refreshDB = function () {
    client.keys('*', function (err, keys) {
        if (!err) {
            keys.forEach(function (key) {
                client.get(key, function (err, data) {
                    if (!err) {
                        livingDB[key] = {
                            status: data,
                            dt: new Date().getTime()
                        }
                    }
                });
            })
        }
    });
    setTimeout(refreshDB, 300000);
};

var purgeDB = function () {
    var ctime = new Date().getTime();
    // livingDB.forEach(function (err, key, data) {
    for (var key in livingDB) {
        if ((livingDB[key].data.dt - ctime) >= 604800000) {
            delete livingDB[key];
            client.del(key);
        }
    }
    // });
    setTimeout(purgeDB, 3594000);
};

refreshDB();
purgeDB();

router.get('/', function (req, res) {
   res.render('index')
});

router.get('/api/alerts', function (req, res, next) {
    res.send(livingDB);
    console.log(livingDB);
});

router.get('*', function (req, res, next) {
    res.status(404).send()
});

module.exports = router;
