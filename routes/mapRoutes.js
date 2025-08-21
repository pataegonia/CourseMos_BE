const express = require('express');
const router = express.Router();
const mapController = require('../controllers/mapController');

router.get('/photos', mapController.getPlacePhotos);

module.exports = router;
