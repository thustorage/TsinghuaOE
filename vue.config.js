const CompressionWebpackPlugin = require('compression-webpack-plugin');

module.exports = {
  'transpileDependencies': ['vuetify'],
  configureWebpack: config => {
    config.plugins.push(new CompressionWebpackPlugin())
  },
  productionSourceMap: process.env.NODE_ENV === 'production' ? false : true,
}