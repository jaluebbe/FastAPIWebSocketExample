import {
    Clock,
    PerspectiveCamera,
    Scene,
    Color,
    Fog,
    HemisphereLight,
    DirectionalLight,
    PlaneGeometry,
    MeshLambertMaterial,
    Mesh,
    SphereGeometry,
    ShaderMaterial,
    BackSide,
    AnimationMixer,
    WebGLRenderer,
    sRGBEncoding
} from 'three';
import {
    GLTFLoader
} from 'three/examples/jsm/loaders/GLTFLoader.js';
let camera, scene, renderer;
const mixers = [];
let stats;
const clock = new Clock();

function initBird(model, period) {
    init(model, period)
    animate();
};
window.initBird = initBird;
export {initBird};

function degrees_to_radians(degrees) {
    var pi = Math.PI;
    return degrees * (pi / 180);
}

function radians_to_degrees(radians) {
    var pi = Math.PI;
    return radians * (180 / pi);
}

function init(model, period) {
    const container = document.getElementById('container');
    container.innerHTML = "";
    camera = new PerspectiveCamera(30, window.innerWidth / window.innerHeight, 1, 5000);
    camera.position.set(0, 0, 250);
    scene = new Scene();
    scene.background = new Color().setHSL(0.6, 0, 1);
    scene.fog = new Fog(scene.background, 1, 5000);

    // LIGHTS
    const hemiLight = new HemisphereLight(0xffffff, 0xffffff, 0.6);
    hemiLight.color.setHSL(0.6, 1, 0.6);
    hemiLight.groundColor.setHSL(0.095, 1, 0.75);
    hemiLight.position.set(0, 50, 0);
    scene.add(hemiLight);

    //
    const dirLight = new DirectionalLight(0xffffff, 1);
    dirLight.color.setHSL(0.1, 1, 0.95);
    dirLight.position.set(-1, 1.75, 1);
    dirLight.position.multiplyScalar(30);
    scene.add(dirLight);
    dirLight.castShadow = true;
    dirLight.shadow.mapSize.width = 2048;
    dirLight.shadow.mapSize.height = 2048;
    const d = 50;
    dirLight.shadow.camera.left = -d;
    dirLight.shadow.camera.right = d;
    dirLight.shadow.camera.top = d;
    dirLight.shadow.camera.bottom = -d;
    dirLight.shadow.camera.far = 3500;
    dirLight.shadow.bias = -0.0001;

    // GROUND
    const groundGeo = new PlaneGeometry(10000, 10000);
    const groundMat = new MeshLambertMaterial({
        color: 0xffffff
    });
    groundMat.color.setHSL(0.095, 1, 0.75);
    const ground = new Mesh(groundGeo, groundMat);
    ground.position.y = -33;
    ground.rotation.x = -Math.PI / 2;
    ground.receiveShadow = true;
    scene.add(ground);

    // SKYDOME
    const vertexShader = "\
				varying vec3 vWorldPosition;\
				void main() {\
    				vec4 worldPosition = modelMatrix * vec4(position, 1.0);\
		    		vWorldPosition = worldPosition.xyz;\
				    gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );\
    		}";
    const fragmentShader = "\
		    uniform vec3 topColor;\
				uniform vec3 bottomColor;\
				uniform float offset;\
				uniform float exponent;\
				varying vec3 vWorldPosition;\
				void main() {\
				    float h = normalize( vWorldPosition + offset ).y;\
						gl_FragColor = vec4( mix( bottomColor, topColor, max( pow( max( h , 0.0), exponent ), 0.0 ) ), 1.0 );\
    		}";

    const uniforms = {
        "topColor": {
            value: new Color(0x0077ff)
        },
        "bottomColor": {
            value: new Color(0xffffff)
        },
        "offset": {
            value: 33
        },
        "exponent": {
            value: 0.6
        }
    };
    uniforms["topColor"].value.copy(hemiLight.color);
    scene.fog.color.copy(uniforms["bottomColor"].value);
    const skyGeo = new SphereGeometry(4000, 32, 15);
    const skyMat = new ShaderMaterial({
        uniforms: uniforms,
        vertexShader: vertexShader,
        fragmentShader: fragmentShader,
        side: BackSide
    });
    const sky = new Mesh(skyGeo, skyMat);
    scene.add(sky);

    // MODEL
    const loader = new GLTFLoader();
    loader.load(model, function(gltf) {
        const mesh = gltf.scene.children[0];
        const s = 0.35;
        mesh.scale.set(s, s, s);
        mesh.position.y = 15;
        mesh.rotation.y = -1;
        mesh.castShadow = true;
        mesh.receiveShadow = true;
        scene.add(mesh);
        mesh.rotation.order = 'YXZ'
        mesh.pitch = function(pitch) {
            if (pitch == undefined) {
                return -radians_to_degrees(mesh.rotation.x);
            } else {
                mesh.rotation.x = -degrees_to_radians(pitch);
            }
        }
        mesh.yaw = function(yaw) {
            if (yaw == undefined) {
                return -radians_to_degrees(mesh.rotation.y);
            } else {
                mesh.rotation.y = -degrees_to_radians(yaw);
            }
        }
        mesh.roll = function(roll) {
            if (roll == undefined) {
                return radians_to_degrees(mesh.rotation.z);
            } else {
                mesh.rotation.z = degrees_to_radians(roll);
            }
        }
        // making bird model accessible from outside the module
        window.bird = mesh;
        const mixer = new AnimationMixer(mesh);
        mixer.clipAction(gltf.animations[0]).setDuration(period).play();
        mixers.push(mixer);
    });

    // RENDERER
    renderer = new WebGLRenderer({
        antialias: true
    });
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(window.innerWidth, window.innerHeight);
    container.appendChild(renderer.domElement);
    renderer.outputEncoding = sRGBEncoding;
    renderer.shadowMap.enabled = true;

    //
    window.addEventListener('resize', onWindowResize);
}

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

function animate() {
    requestAnimationFrame(animate);
    render();
}

function render() {
    const delta = clock.getDelta();
    for (let i = 0; i < mixers.length; i++) {
        mixers[i].update(delta);
    }
    renderer.render(scene, camera);
}
