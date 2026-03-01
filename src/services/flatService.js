import pool from '../config/database.js';

class FlatService {
  /**
   * Create a new flat
   * @param {string} name - Flat name
   * @param {string} createdBy - User ID of the creator
   * @returns {Promise<Object>} Created flat object
   */
  async createFlat(name, createdBy) {
    const client = await pool.connect();
    
    try {
      await client.query('BEGIN');

      // Create the flat
      const flatResult = await client.query(
        `INSERT INTO flats (name, created_by)
         VALUES ($1, $2)
         RETURNING id, name, created_by, created_at, updated_at`,
        [name, createdBy]
      );

      const flat = flatResult.rows[0];

      // Automatically add the creator as a member
      await client.query(
        `INSERT INTO flat_members (flat_id, user_id)
         VALUES ($1, $2)`,
        [flat.id, createdBy]
      );

      await client.query('COMMIT');

      return flat;
    } catch (error) {
      await client.query('ROLLBACK');
      throw error;
    } finally {
      client.release();
    }
  }

  /**
   * Get all flats for a user
   * @param {string} userId - User ID
   * @returns {Promise<Array>} Array of flats the user belongs to
   */
  async getUserFlats(userId) {
    const result = await pool.query(
      `SELECT f.id, f.name, f.created_by, f.created_at, f.updated_at,
              fm.joined_at
       FROM flats f
       INNER JOIN flat_members fm ON f.id = fm.flat_id
       WHERE fm.user_id = $1
       ORDER BY f.created_at DESC`,
      [userId]
    );

    return result.rows;
  }

  /**
   * Get flat by ID
   * @param {string} flatId - Flat ID
   * @returns {Promise<Object>} Flat object
   */
  async getFlatById(flatId) {
    const result = await pool.query(
      `SELECT id, name, created_by, created_at, updated_at
       FROM flats
       WHERE id = $1`,
      [flatId]
    );

    if (result.rows.length === 0) {
      const error = new Error('Flat not found');
      error.statusCode = 404;
      throw error;
    }

    return result.rows[0];
  }

  /**
   * Get all members of a flat
   * @param {string} flatId - Flat ID
   * @returns {Promise<Array>} Array of flat members
   */
  async getFlatMembers(flatId) {
    const result = await pool.query(
      `SELECT u.id, u.email, u.name, fm.joined_at
       FROM users u
       INNER JOIN flat_members fm ON u.id = fm.user_id
       WHERE fm.flat_id = $1
       ORDER BY fm.joined_at ASC`,
      [flatId]
    );

    return result.rows;
  }

  /**
   * Add a member to a flat
   * @param {string} flatId - Flat ID
   * @param {string} userId - User ID to add
   * @returns {Promise<Object>} Created flat member record
   */
  async addMemberToFlat(flatId, userId) {
    // Check if flat exists
    await this.getFlatById(flatId);

    // Check if user exists
    const userResult = await pool.query(
      'SELECT id FROM users WHERE id = $1',
      [userId]
    );

    if (userResult.rows.length === 0) {
      const error = new Error('User not found');
      error.statusCode = 404;
      throw error;
    }

    // Check if user is already a member
    const existingMember = await pool.query(
      'SELECT id FROM flat_members WHERE flat_id = $1 AND user_id = $2',
      [flatId, userId]
    );

    if (existingMember.rows.length > 0) {
      const error = new Error('User is already a member of this flat');
      error.statusCode = 409;
      throw error;
    }

    // Add member
    const result = await pool.query(
      `INSERT INTO flat_members (flat_id, user_id)
       VALUES ($1, $2)
       RETURNING id, flat_id, user_id, joined_at`,
      [flatId, userId]
    );

    return result.rows[0];
  }

  /**
   * Check if a user is a member of a flat
   * @param {string} flatId - Flat ID
   * @param {string} userId - User ID
   * @returns {Promise<boolean>} True if user is a member
   */
  async isUserMemberOfFlat(flatId, userId) {
    const result = await pool.query(
      'SELECT id FROM flat_members WHERE flat_id = $1 AND user_id = $2',
      [flatId, userId]
    );

    return result.rows.length > 0;
  }

  /**
   * Remove a member from a flat
   * @param {string} flatId - Flat ID
   * @param {string} userId - User ID to remove
   * @returns {Promise<void>}
   */
  async removeMemberFromFlat(flatId, userId) {
    // Check if flat exists
    await this.getFlatById(flatId);

    // Check if user is a member
    const isMember = await this.isUserMemberOfFlat(flatId, userId);
    
    if (!isMember) {
      const error = new Error('User is not a member of this flat');
      error.statusCode = 404;
      throw error;
    }

    // Remove member
    await pool.query(
      'DELETE FROM flat_members WHERE flat_id = $1 AND user_id = $2',
      [flatId, userId]
    );
  }
}

export default new FlatService();
