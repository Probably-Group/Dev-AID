## 7. Performance Patterns

### 6.1 Buffer Reuse

```typescript
// Bad - Creates new buffer every frame
const buffer = gl.createBuffer()
gl.bufferData(gl.ARRAY_BUFFER, data, gl.DYNAMIC_DRAW)
gl.deleteBuffer(buffer)

// Good - Reuse buffer, update only data
gl.bufferSubData(gl.ARRAY_BUFFER, 0, data)  // Update existing buffer
```

### 6.2 Draw Call Batching

```typescript
// Bad - One draw call per object
objects.forEach(obj => {
  gl.useProgram(obj.program)
  gl.drawElements(...)
})

// Good - Batch by material/shader
const batches = groupByMaterial(objects)
batches.forEach(batch => {
  gl.useProgram(batch.program)
  batch.objects.forEach(obj => gl.drawElements(...))
})
```

### 6.3 Texture Compression

```typescript
// Bad - Always uncompressed RGBA
gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, image)

// Good - Use compressed formats when available
const ext = gl.getExtension('WEBGL_compressed_texture_s3tc')
if (ext) gl.compressedTexImage2D(gl.TEXTURE_2D, 0, ext.COMPRESSED_RGBA_S3TC_DXT5_EXT, ...)
```

### 6.4 Instanced Rendering

```typescript
// Bad - Individual draw calls for particles
particles.forEach(p => {
  gl.uniform3fv(uPosition, p.position)
  gl.drawArrays(gl.TRIANGLES, 0, 6)
})

// Good - Single instanced draw call
gl.drawArraysInstanced(gl.TRIANGLES, 0, 6, particles.length)
```

### 6.5 VAO Usage

```typescript
// Bad - Rebind attributes every frame
gl.enableVertexAttribArray(0)
gl.vertexAttribPointer(0, 3, gl.FLOAT, false, 0, 0)

// Good - Use VAO to store attribute state
const vao = gl.createVertexArray()
gl.bindVertexArray(vao)
// Set up once, then just bind VAO for rendering
```

