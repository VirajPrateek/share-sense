import flatService from './flatService.js';
import pool from '../config/database.js';

describe('FlatService', () => {
  let testUser1, testUser2;

  beforeAll(async () => {
    // Create test users
    const user1Result = await pool.query(
      `INSERT INTO users (email, password_hash, name)
       VALUES ($1, $2, $3)
       RETURNING id, email, name`,
      ['flattest1@example.com', 'hash1', 'Test User 1']
    );
    testUser1 = user1Result.rows[0];

    const user2Result = await pool.query(
      `INSERT INTO users (email, password_hash, name)
       VALUES ($1, $2, $3)
       RETURNING id, email, name`,
      ['flattest2@example.com', 'hash2', 'Test User 2']
    );
    testUser2 = user2Result.rows[0];
  });

  afterAll(async () => {
    // Clean up test data
    await pool.query('DELETE FROM users WHERE email LIKE $1', ['flattest%@example.com']);
    await pool.end();
  });

  describe('createFlat', () => {
    it('should create a flat and add creator as member', async () => {
      const flat = await flatService.createFlat('Test Flat', testUser1.id);

      expect(flat).toBeDefined();
      expect(flat.id).toBeDefined();
      expect(flat.name).toBe('Test Flat');
      expect(flat.created_by).toBe(testUser1.id);

      // Verify creator is a member
      const members = await flatService.getFlatMembers(flat.id);
      expect(members).toHaveLength(1);
      expect(members[0].id).toBe(testUser1.id);

      // Clean up
      await pool.query('DELETE FROM flats WHERE id = $1', [flat.id]);
    });

    it('should create multiple flats for the same user', async () => {
      const flat1 = await flatService.createFlat('Flat 1', testUser1.id);
      const flat2 = await flatService.createFlat('Flat 2', testUser1.id);

      expect(flat1.id).not.toBe(flat2.id);
      expect(flat1.name).toBe('Flat 1');
      expect(flat2.name).toBe('Flat 2');

      // Clean up
      await pool.query('DELETE FROM flats WHERE id IN ($1, $2)', [flat1.id, flat2.id]);
    });
  });

  describe('getUserFlats', () => {
    let testFlat1, testFlat2;

    beforeEach(async () => {
      testFlat1 = await flatService.createFlat('User Flat 1', testUser1.id);
      testFlat2 = await flatService.createFlat('User Flat 2', testUser1.id);
    });

    afterEach(async () => {
      await pool.query('DELETE FROM flats WHERE id IN ($1, $2)', [testFlat1.id, testFlat2.id]);
    });

    it('should return all flats for a user', async () => {
      const flats = await flatService.getUserFlats(testUser1.id);

      expect(flats.length).toBeGreaterThanOrEqual(2);
      const flatIds = flats.map(f => f.id);
      expect(flatIds).toContain(testFlat1.id);
      expect(flatIds).toContain(testFlat2.id);
    });

    it('should return empty array for user with no flats', async () => {
      const flats = await flatService.getUserFlats(testUser2.id);
      expect(flats).toEqual([]);
    });

    it('should include joined_at timestamp', async () => {
      const flats = await flatService.getUserFlats(testUser1.id);
      const flat = flats.find(f => f.id === testFlat1.id);
      
      expect(flat.joined_at).toBeDefined();
      expect(flat.joined_at).toBeInstanceOf(Date);
    });
  });

  describe('getFlatById', () => {
    let testFlat;

    beforeEach(async () => {
      testFlat = await flatService.createFlat('Get By ID Flat', testUser1.id);
    });

    afterEach(async () => {
      await pool.query('DELETE FROM flats WHERE id = $1', [testFlat.id]);
    });

    it('should return flat by ID', async () => {
      const flat = await flatService.getFlatById(testFlat.id);

      expect(flat).toBeDefined();
      expect(flat.id).toBe(testFlat.id);
      expect(flat.name).toBe('Get By ID Flat');
      expect(flat.created_by).toBe(testUser1.id);
    });

    it('should throw error for non-existent flat', async () => {
      const fakeId = '00000000-0000-0000-0000-000000000000';
      
      await expect(flatService.getFlatById(fakeId)).rejects.toThrow('Flat not found');
    });
  });

  describe('getFlatMembers', () => {
    let testFlat;

    beforeEach(async () => {
      testFlat = await flatService.createFlat('Members Flat', testUser1.id);
    });

    afterEach(async () => {
      await pool.query('DELETE FROM flats WHERE id = $1', [testFlat.id]);
    });

    it('should return all members of a flat', async () => {
      // Add second user
      await flatService.addMemberToFlat(testFlat.id, testUser2.id);

      const members = await flatService.getFlatMembers(testFlat.id);

      expect(members).toHaveLength(2);
      expect(members[0].id).toBe(testUser1.id);
      expect(members[1].id).toBe(testUser2.id);
    });

    it('should include user details in member list', async () => {
      const members = await flatService.getFlatMembers(testFlat.id);

      expect(members[0]).toHaveProperty('id');
      expect(members[0]).toHaveProperty('email');
      expect(members[0]).toHaveProperty('name');
      expect(members[0]).toHaveProperty('joined_at');
    });

    it('should return empty array for flat with no members', async () => {
      // Create flat and remove creator
      const emptyFlat = await flatService.createFlat('Empty Flat', testUser1.id);
      await pool.query('DELETE FROM flat_members WHERE flat_id = $1', [emptyFlat.id]);

      const members = await flatService.getFlatMembers(emptyFlat.id);
      expect(members).toEqual([]);

      // Clean up
      await pool.query('DELETE FROM flats WHERE id = $1', [emptyFlat.id]);
    });
  });

  describe('addMemberToFlat', () => {
    let testFlat;

    beforeEach(async () => {
      testFlat = await flatService.createFlat('Add Member Flat', testUser1.id);
    });

    afterEach(async () => {
      await pool.query('DELETE FROM flats WHERE id = $1', [testFlat.id]);
    });

    it('should add a member to a flat', async () => {
      const member = await flatService.addMemberToFlat(testFlat.id, testUser2.id);

      expect(member).toBeDefined();
      expect(member.flat_id).toBe(testFlat.id);
      expect(member.user_id).toBe(testUser2.id);
      expect(member.joined_at).toBeDefined();

      // Verify member was added
      const members = await flatService.getFlatMembers(testFlat.id);
      expect(members).toHaveLength(2);
    });

    it('should throw error when adding non-existent user', async () => {
      const fakeUserId = '00000000-0000-0000-0000-000000000000';
      
      await expect(
        flatService.addMemberToFlat(testFlat.id, fakeUserId)
      ).rejects.toThrow('User not found');
    });

    it('should throw error when adding to non-existent flat', async () => {
      const fakeFlatId = '00000000-0000-0000-0000-000000000000';
      
      await expect(
        flatService.addMemberToFlat(fakeFlatId, testUser2.id)
      ).rejects.toThrow('Flat not found');
    });

    it('should throw error when adding duplicate member', async () => {
      await flatService.addMemberToFlat(testFlat.id, testUser2.id);
      
      await expect(
        flatService.addMemberToFlat(testFlat.id, testUser2.id)
      ).rejects.toThrow('User is already a member of this flat');
    });
  });

  describe('isUserMemberOfFlat', () => {
    let testFlat;

    beforeEach(async () => {
      testFlat = await flatService.createFlat('Membership Check Flat', testUser1.id);
    });

    afterEach(async () => {
      await pool.query('DELETE FROM flats WHERE id = $1', [testFlat.id]);
    });

    it('should return true for flat member', async () => {
      const isMember = await flatService.isUserMemberOfFlat(testFlat.id, testUser1.id);
      expect(isMember).toBe(true);
    });

    it('should return false for non-member', async () => {
      const isMember = await flatService.isUserMemberOfFlat(testFlat.id, testUser2.id);
      expect(isMember).toBe(false);
    });
  });

  describe('removeMemberFromFlat', () => {
    let testFlat;

    beforeEach(async () => {
      testFlat = await flatService.createFlat('Remove Member Flat', testUser1.id);
      await flatService.addMemberToFlat(testFlat.id, testUser2.id);
    });

    afterEach(async () => {
      await pool.query('DELETE FROM flats WHERE id = $1', [testFlat.id]);
    });

    it('should remove a member from a flat', async () => {
      await flatService.removeMemberFromFlat(testFlat.id, testUser2.id);

      const members = await flatService.getFlatMembers(testFlat.id);
      expect(members).toHaveLength(1);
      expect(members[0].id).toBe(testUser1.id);
    });

    it('should throw error when removing non-member', async () => {
      // Create another user
      const user3Result = await pool.query(
        `INSERT INTO users (email, password_hash, name)
         VALUES ($1, $2, $3)
         RETURNING id`,
        ['flattest3@example.com', 'hash3', 'Test User 3']
      );
      const testUser3 = user3Result.rows[0];

      await expect(
        flatService.removeMemberFromFlat(testFlat.id, testUser3.id)
      ).rejects.toThrow('User is not a member of this flat');

      // Clean up
      await pool.query('DELETE FROM users WHERE id = $1', [testUser3.id]);
    });

    it('should throw error when removing from non-existent flat', async () => {
      const fakeFlatId = '00000000-0000-0000-0000-000000000000';
      
      await expect(
        flatService.removeMemberFromFlat(fakeFlatId, testUser2.id)
      ).rejects.toThrow('Flat not found');
    });
  });

  describe('Multi-flat membership', () => {
    let flat1, flat2, flat3;

    beforeEach(async () => {
      flat1 = await flatService.createFlat('Multi Flat 1', testUser1.id);
      flat2 = await flatService.createFlat('Multi Flat 2', testUser2.id);
      flat3 = await flatService.createFlat('Multi Flat 3', testUser1.id);
    });

    afterEach(async () => {
      await pool.query('DELETE FROM flats WHERE id IN ($1, $2, $3)', [flat1.id, flat2.id, flat3.id]);
    });

    it('should allow user to belong to multiple flats', async () => {
      // Add testUser1 to flat2
      await flatService.addMemberToFlat(flat2.id, testUser1.id);

      const flats = await flatService.getUserFlats(testUser1.id);
      const flatIds = flats.map(f => f.id);

      expect(flatIds).toContain(flat1.id);
      expect(flatIds).toContain(flat2.id);
      expect(flatIds).toContain(flat3.id);
    });

    it('should maintain separate member lists for each flat', async () => {
      // Add testUser2 to flat1
      await flatService.addMemberToFlat(flat1.id, testUser2.id);

      const flat1Members = await flatService.getFlatMembers(flat1.id);
      const flat2Members = await flatService.getFlatMembers(flat2.id);

      expect(flat1Members).toHaveLength(2);
      expect(flat2Members).toHaveLength(1);
    });
  });
});
