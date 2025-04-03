from owslib.wms import WebMapService

def wms_interrogate(url):

    # wms = WebMapService(url)

    try:
        wms = WebMapService(url)
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    print(wms.identification.type)
    print(wms.identification.version)
    print(wms.identification.title)
    print(wms.identification.abstract)

    # for illo in wms.items():
    #     # print(illo[0].split(':')[1])
    #     print(illo)

    print(wms.contents.items())
    print(wms.contents.keys())
    print(wms.contents.values())
    # print(wms.contents.fromkeys(wms.contents.keys()))

    # for layer in wms.contents:
    #     print(layer)
    #     # print(layer.name)
    #     # print(layer.title)
    #     # print(layer.abstract)
    #     # print(layer.boundingBox)


if __name__ == '__main__':
    wms_interrogate('https://geoportale.comune.roma.it/geoserver/ows?service=WMS')

