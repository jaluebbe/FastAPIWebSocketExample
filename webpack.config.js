module.exports = {
    mode: 'production',
    experiments: {
        outputModule: true,
    },
    output: {
        filename: 'bird.js',
        path: __dirname + '/backend/static',
        library: {
            type: 'module'
        }
    },
    performance: {
        maxEntrypointSize: 1024000,
        maxAssetSize: 1024000
    }
}
