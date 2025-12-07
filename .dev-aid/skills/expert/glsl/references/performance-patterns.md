## 6. Performance Patterns

### 5.1 Avoid Branching - Use Mix/Step

```glsl
// ❌ BAD - GPU branch divergence
vec3 getColor(float value) {
  if (value < 0.3) {
    return vec3(1.0, 0.0, 0.0);  // Red
  } else if (value < 0.7) {
    return vec3(1.0, 1.0, 0.0);  // Yellow
  } else {
    return vec3(0.0, 1.0, 0.0);  // Green
  }
}

// ✅ GOOD - Branchless with mix/step
vec3 getColor(float value) {
  vec3 red = vec3(1.0, 0.0, 0.0);
  vec3 yellow = vec3(1.0, 1.0, 0.0);
  vec3 green = vec3(0.0, 1.0, 0.0);

  vec3 color = mix(red, yellow, smoothstep(0.3, 0.31, value));
  color = mix(color, green, smoothstep(0.7, 0.71, value));
  return color;
}
```

### 5.2 Texture Atlases - Reduce Draw Calls

```glsl
// ❌ BAD - Multiple texture bindings
uniform sampler2D uIcon1;
uniform sampler2D uIcon2;
uniform sampler2D uIcon3;

vec4 getIcon(int id) {
  if (id == 0) return texture(uIcon1, vUv);
  if (id == 1) return texture(uIcon2, vUv);
  return texture(uIcon3, vUv);
}

// ✅ GOOD - Single atlas texture
uniform sampler2D uIconAtlas;
uniform vec4 uAtlasOffsets[3];  // [x, y, width, height] for each icon

vec4 getIcon(int id) {
  vec4 offset = uAtlasOffsets[id];
  vec2 atlasUV = offset.xy + vUv * offset.zw;
  return texture(uIconAtlas, atlasUV);
}
```

### 5.3 Level of Detail (LOD) - Distance-Based Quality

```glsl
// ❌ BAD - Same quality regardless of distance
const int NOISE_OCTAVES = 8;

float noise(vec3 p) {
  float result = 0.0;
  for (int i = 0; i < NOISE_OCTAVES; i++) {
    result += snoise(p * pow(2.0, float(i)));
  }
  return result;
}

// ✅ GOOD - Reduce octaves based on distance
uniform float uCameraDistance;

float noise(vec3 p) {
  // Fewer octaves when far away (detail not visible)
  int octaves = int(mix(2.0, 8.0, 1.0 - smoothstep(10.0, 100.0, uCameraDistance)));
  float result = 0.0;
  for (int i = 0; i < 8; i++) {
    if (i >= octaves) break;
    result += snoise(p * pow(2.0, float(i)));
  }
  return result;
}
```

### 5.4 Uniform Batching - Minimize CPU-GPU Transfers

```glsl
// ❌ BAD - Many individual uniforms
uniform float uPosX;
uniform float uPosY;
uniform float uPosZ;
uniform float uRotX;
uniform float uRotY;
uniform float uRotZ;
uniform float uScaleX;
uniform float uScaleY;
uniform float uScaleZ;

// ✅ GOOD - Packed into vectors/matrices
uniform vec3 uPosition;
uniform vec3 uRotation;
uniform vec3 uScale;
// Or even better:
uniform mat4 uTransform;
```

### 5.5 Precision Optimization - Use Appropriate Precision

```glsl
// ❌ BAD - Everything highp (wastes GPU cycles)
precision highp float;

highp vec3 color;
highp float alpha;
highp vec2 uv;

// ✅ GOOD - Match precision to data needs
precision highp float;  // Default for calculations

mediump vec3 color;     // 0-1 range, mediump sufficient
mediump float alpha;    // 0-1 range
highp vec2 uv;          // Need precision for texture coords
lowp int flags;         // Boolean-like values
```

### 5.6 Cache Texture Lookups

```glsl
// ❌ BAD - Redundant texture fetches
void main() {
  vec3 diffuse = texture(uTexture, vUv).rgb;
  // ... some code ...
  float alpha = texture(uTexture, vUv).a;  // Same lookup!
  // ... more code ...
  vec3 doubled = texture(uTexture, vUv).rgb * 2.0;  // Again!
}

// ✅ GOOD - Cache the result
void main() {
  vec4 texSample = texture(uTexture, vUv);
  vec3 diffuse = texSample.rgb;
  float alpha = texSample.a;
  vec3 doubled = texSample.rgb * 2.0;
}
```

