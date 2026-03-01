import request from 'supertest';
import app from '../app.js';
import pool from '../config/database.js';
import authService from '../services/authService.js';

describe('Flat Routes', () => {
  let testUser1, testUser2, token1, token2;

  beforeAll(async () => {
    // Create test users
    testUser1 = await authService.register(
      'flatroutes1@example.com',
      'password123',
      'Flat Routes User 1'
    );
    testUser2 = await authService.register(
      'flatroutes2@example.com',
      'password123',
      'Flat Routes User 2'
    );

    // Get tokens
    const login1 = await authService.login('flatroutes1@example.com', 'password123');
    const login2 = await authService.login('flatroutes2@example.com', 'password123');
    token1 = login1.token;
    token2 = login2.token;
  });

  afterAll(async () => {
    // Clean up test data
    await pool.query('DELETE FROM users WHERE email LIKE $1', ['flatroutes%@example.com']);
    await pool.end();
  });

  describe('POST /api/flats', () => {
    it('should create a flat with valid data', async () => {
      const response = await request(app)
        .post('/api/flats')
        .set('Authorization', `Bearer ${token1}`)
        .send({ name: 'Test Flat' });

      expect(response.status).toBe(201);
      expect(response.body.message).toBe('Flat created successfully');
      expect(response.body.flat).toBeDefined();
      expect(response.body.flat.name).toBe('Test Flat');
      expect(response.body.flat.created_by).toBe(testUser1.id);

      // Clean up
      await pool.query('DELETE FROM flats WHERE id = $1', [response.body.flat.id]);
    });

    it('should reject request without authentication', async () => {
      const response = await request(app)
        .post('/api/flats')
        .send({ name: 'Test Flat' });

      expect(response.status).toBe(401);
    });

    it('should reject request without flat name', async () => {
      const response = await request(app)
        .post('/api/flats')
        .set('Authorization', `Bearer ${token1}`)
        .send({});

      expect(response.status).toBe(400);
      expect(response.body.message).toBe('Flat name is required');
    });

    it('should reject request with empty flat name', async () => {
      const response = await request(app)
        .post('/api/flats')
        .set('Authorization', `Bearer ${token1}`)
        .send({ name: '   ' });

      expect(response.status).toBe(400);
      expect(response.body.message).toBe('Flat name is required');
    });
  });

  describe('GET /api/flats', () => {
    let testFlat1, testFlat2;

    beforeEach(async () => {
      // Create test flats
      const response1 = await request(app)
        .post('/api/flats')
        .set('Authorization', `Bearer ${token1}`)
        .send({ name: 'User 1 Flat 1' });
      testFlat1 = response1.body.flat;

      const response2 = await request(app)
        .post('/api/flats')
        .set('Authorization', `Bearer ${token1}`)
        .send({ name: 'User 1 Flat 2' });
      testFlat2 = response2.body.flat;
    });

    afterEach(async () => {
      await pool.query('DELETE FROM flats WHERE id IN ($1, $2)', [testFlat1.id, testFlat2.id]);
    });

    it('should return all flats for authenticated user', async () => {
      const response = await request(app)
        .get('/api/flats')
        .set('Authorization', `Bearer ${token1}`);

      expect(response.status).toBe(200);
      expect(response.body.flats).toBeDefined();
      expect(Array.isArray(response.body.flats)).toBe(true);
      expect(response.body.flats.length).toBeGreaterThanOrEqual(2);

      const flatIds = response.body.flats.map(f => f.id);
      expect(flatIds).toContain(testFlat1.id);
      expect(flatIds).toContain(testFlat2.id);
    });

    it('should reject request without authentication', async () => {
      const response = await request(app).get('/api/flats');

      expect(response.status).toBe(401);
    });

    it('should return empty array for user with no flats', async () => {
      const response = await request(app)
        .get('/api/flats')
        .set('Authorization', `Bearer ${token2}`);

      expect(response.status).toBe(200);
      expect(response.body.flats).toEqual([]);
    });
  });

  describe('GET /api/flats/:flatId', () => {
    let testFlat;

    beforeEach(async () => {
      const response = await request(app)
        .post('/api/flats')
        .set('Authorization', `Bearer ${token1}`)
        .send({ name: 'Get Flat Test' });
      testFlat = response.body.flat;
    });

    afterEach(async () => {
      await pool.query('DELETE FROM flats WHERE id = $1', [testFlat.id]);
    });

    it('should return flat details for member', async () => {
      const response = await request(app)
        .get(`/api/flats/${testFlat.id}`)
        .set('Authorization', `Bearer ${token1}`);

      expect(response.status).toBe(200);
      expect(response.body.flat).toBeDefined();
      expect(response.body.flat.id).toBe(testFlat.id);
      expect(response.body.flat.name).toBe('Get Flat Test');
    });

    it('should reject access for non-member', async () => {
      const response = await request(app)
        .get(`/api/flats/${testFlat.id}`)
        .set('Authorization', `Bearer ${token2}`);

      expect(response.status).toBe(403);
      expect(response.body.message).toBe('You are not a member of this flat');
    });

    it('should return 404 for non-existent flat', async () => {
      const fakeId = '00000000-0000-0000-0000-000000000000';
      const response = await request(app)
        .get(`/api/flats/${fakeId}`)
        .set('Authorization', `Bearer ${token1}`);

      expect(response.status).toBe(404);
    });
  });

  describe('GET /api/flats/:flatId/members', () => {
    let testFlat;

    beforeEach(async () => {
      const response = await request(app)
        .post('/api/flats')
        .set('Authorization', `Bearer ${token1}`)
        .send({ name: 'Members Test Flat' });
      testFlat = response.body.flat;
    });

    afterEach(async () => {
      await pool.query('DELETE FROM flats WHERE id = $1', [testFlat.id]);
    });

    it('should return flat members for member', async () => {
      const response = await request(app)
        .get(`/api/flats/${testFlat.id}/members`)
        .set('Authorization', `Bearer ${token1}`);

      expect(response.status).toBe(200);
      expect(response.body.members).toBeDefined();
      expect(Array.isArray(response.body.members)).toBe(true);
      expect(response.body.members).toHaveLength(1);
      expect(response.body.members[0].id).toBe(testUser1.id);
    });

    it('should reject access for non-member', async () => {
      const response = await request(app)
        .get(`/api/flats/${testFlat.id}/members`)
        .set('Authorization', `Bearer ${token2}`);

      expect(response.status).toBe(403);
      expect(response.body.message).toBe('You are not a member of this flat');
    });
  });

  describe('POST /api/flats/:flatId/members', () => {
    let testFlat;

    beforeEach(async () => {
      const response = await request(app)
        .post('/api/flats')
        .set('Authorization', `Bearer ${token1}`)
        .send({ name: 'Add Member Test Flat' });
      testFlat = response.body.flat;
    });

    afterEach(async () => {
      await pool.query('DELETE FROM flats WHERE id = $1', [testFlat.id]);
    });

    it('should add member to flat', async () => {
      const response = await request(app)
        .post(`/api/flats/${testFlat.id}/members`)
        .set('Authorization', `Bearer ${token1}`)
        .send({ userId: testUser2.id });

      expect(response.status).toBe(201);
      expect(response.body.message).toBe('Member added successfully');
      expect(response.body.member).toBeDefined();
      expect(response.body.member.user_id).toBe(testUser2.id);

      // Verify member was added
      const membersResponse = await request(app)
        .get(`/api/flats/${testFlat.id}/members`)
        .set('Authorization', `Bearer ${token1}`);

      expect(membersResponse.body.members).toHaveLength(2);
    });

    it('should reject request without userId', async () => {
      const response = await request(app)
        .post(`/api/flats/${testFlat.id}/members`)
        .set('Authorization', `Bearer ${token1}`)
        .send({});

      expect(response.status).toBe(400);
      expect(response.body.message).toBe('User ID is required');
    });

    it('should reject adding duplicate member', async () => {
      // Add member first time
      await request(app)
        .post(`/api/flats/${testFlat.id}/members`)
        .set('Authorization', `Bearer ${token1}`)
        .send({ userId: testUser2.id });

      // Try to add again
      const response = await request(app)
        .post(`/api/flats/${testFlat.id}/members`)
        .set('Authorization', `Bearer ${token1}`)
        .send({ userId: testUser2.id });

      expect(response.status).toBe(409);
      expect(response.body.error).toBe('User is already a member of this flat');
    });

    it('should reject access for non-member', async () => {
      const response = await request(app)
        .post(`/api/flats/${testFlat.id}/members`)
        .set('Authorization', `Bearer ${token2}`)
        .send({ userId: testUser2.id });

      expect(response.status).toBe(403);
      expect(response.body.message).toBe('You are not a member of this flat');
    });
  });

  describe('DELETE /api/flats/:flatId/members/:userId', () => {
    let testFlat;

    beforeEach(async () => {
      const response = await request(app)
        .post('/api/flats')
        .set('Authorization', `Bearer ${token1}`)
        .send({ name: 'Remove Member Test Flat' });
      testFlat = response.body.flat;

      // Add second user
      await request(app)
        .post(`/api/flats/${testFlat.id}/members`)
        .set('Authorization', `Bearer ${token1}`)
        .send({ userId: testUser2.id });
    });

    afterEach(async () => {
      await pool.query('DELETE FROM flats WHERE id = $1', [testFlat.id]);
    });

    it('should remove member from flat', async () => {
      const response = await request(app)
        .delete(`/api/flats/${testFlat.id}/members/${testUser2.id}`)
        .set('Authorization', `Bearer ${token1}`);

      expect(response.status).toBe(200);
      expect(response.body.message).toBe('Member removed successfully');

      // Verify member was removed
      const membersResponse = await request(app)
        .get(`/api/flats/${testFlat.id}/members`)
        .set('Authorization', `Bearer ${token1}`);

      expect(membersResponse.body.members).toHaveLength(1);
      expect(membersResponse.body.members[0].id).toBe(testUser1.id);
    });

    it('should reject removing non-existent member', async () => {
      const fakeUserId = '00000000-0000-0000-0000-000000000000';
      const response = await request(app)
        .delete(`/api/flats/${testFlat.id}/members/${fakeUserId}`)
        .set('Authorization', `Bearer ${token1}`);

      expect(response.status).toBe(404);
      expect(response.body.error).toBe('User is not a member of this flat');
    });

    it('should reject access for non-member', async () => {
      // Create another flat for user2
      const response2 = await request(app)
        .post('/api/flats')
        .set('Authorization', `Bearer ${token2}`)
        .send({ name: 'User 2 Flat' });
      const user2Flat = response2.body.flat;

      // Try to remove member from user1's flat
      const response = await request(app)
        .delete(`/api/flats/${testFlat.id}/members/${testUser2.id}`)
        .set('Authorization', `Bearer ${token2}`);

      expect(response.status).toBe(403);
      expect(response.body.message).toBe('You are not a member of this flat');

      // Clean up
      await pool.query('DELETE FROM flats WHERE id = $1', [user2Flat.id]);
    });
  });

  describe('Multi-flat membership', () => {
    let flat1, flat2;

    beforeEach(async () => {
      const response1 = await request(app)
        .post('/api/flats')
        .set('Authorization', `Bearer ${token1}`)
        .send({ name: 'Multi Flat 1' });
      flat1 = response1.body.flat;

      const response2 = await request(app)
        .post('/api/flats')
        .set('Authorization', `Bearer ${token2}`)
        .send({ name: 'Multi Flat 2' });
      flat2 = response2.body.flat;
    });

    afterEach(async () => {
      await pool.query('DELETE FROM flats WHERE id IN ($1, $2)', [flat1.id, flat2.id]);
    });

    it('should allow user to join multiple flats', async () => {
      // Add user1 to flat2
      await request(app)
        .post(`/api/flats/${flat2.id}/members`)
        .set('Authorization', `Bearer ${token2}`)
        .send({ userId: testUser1.id });

      // Get user1's flats
      const response = await request(app)
        .get('/api/flats')
        .set('Authorization', `Bearer ${token1}`);

      const flatIds = response.body.flats.map(f => f.id);
      expect(flatIds).toContain(flat1.id);
      expect(flatIds).toContain(flat2.id);
    });

    it('should allow user to access all their flats', async () => {
      // Add user1 to flat2
      await request(app)
        .post(`/api/flats/${flat2.id}/members`)
        .set('Authorization', `Bearer ${token2}`)
        .send({ userId: testUser1.id });

      // User1 should be able to access both flats
      const response1 = await request(app)
        .get(`/api/flats/${flat1.id}`)
        .set('Authorization', `Bearer ${token1}`);
      expect(response1.status).toBe(200);

      const response2 = await request(app)
        .get(`/api/flats/${flat2.id}`)
        .set('Authorization', `Bearer ${token1}`);
      expect(response2.status).toBe(200);
    });
  });
});
