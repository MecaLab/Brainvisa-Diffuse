cmake_minimum_required( VERSION 2.6 )

find_package( python REQUIRED )
find_package( brainvisa-cmake REQUIRED )


BRAINVISA_PROJECT()

BRAINVISA_COPY_PYTHON_DIRECTORY( "${CMAKE_CURRENT_SOURCE_DIR}/brainvisa"
                                 ${PROJECT_NAME} )

BRAINVISA_COPY_PYTHON_DIRECTORY( "${CMAKE_CURRENT_SOURCE_DIR}/python"
                                 ${PROJECT_NAME} )  

BRAINVISA_COPY_DIRECTORY( "${CMAKE_CURRENT_SOURCE_DIR}/share"
                          "share"
                          ${PROJECT_NAME} )

