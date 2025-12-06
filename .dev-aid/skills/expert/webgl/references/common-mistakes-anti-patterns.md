## 9. Common Mistakes & Anti-Patterns

### 8.1 Critical Security Anti-Patterns

#### Never: Skip Context Loss Handling

```typescript
// ❌ DANGEROUS - App crashes on context loss
const gl = canvas.getContext('webgl2')
// No context loss handler!

// ✅ SECURE - Handle gracefully
canvas.addEventListener('webglcontextlost', handleLoss)
canvas.addEventListener('webglcontextrestored', handleRestore)
```

#### Never: Unlimited Resource Allocation

```typescript
// ❌ DANGEROUS - GPU memory exhaustion
for (let i = 0; i < userCount; i++) {
  textures.push(gl.createTexture())
}

// ✅ SECURE - Enforce limits
if (textureCount < MAX_TEXTURES) {
  textures.push(gl.createTexture())
}
```

### 8.2 Performance Anti-Patterns

#### Avoid: Excessive State Changes

```typescript
// ❌ BAD - Unbatched draw calls
objects.forEach(obj => {
  gl.useProgram(obj.program)
  gl.bindTexture(gl.TEXTURE_2D, obj.texture)
  gl.drawElements(...)
})

// ✅ GOOD - Batch by material
batches.forEach(batch => {
  gl.useProgram(batch.program)
  gl.bindTexture(gl.TEXTURE_2D, batch.texture)
  batch.objects.forEach(obj => gl.drawElements(...))
})
```

