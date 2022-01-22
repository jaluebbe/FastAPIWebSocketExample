module.exports = {
    experiments: {
        outputModule: true,
    },
    output: {
        filename: 'bird.js',
        library: {
            type: 'module'
        }
//        libraryTarget: 'commonjs-module'
    }
}
