import qbs

Project {

    references: [
        "Physics/Physics.qbs",
        "QPhysics/QPhysics.qbs",
        "QPhysicsUI/QPhysicsUI.qbs",
        "QPhysicsDesigner/QPhysicsDesigner.qbs"
    ]


    Product {
        name: "CodeGen"



    }
}
