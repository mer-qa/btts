<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

    <xsl:template match="node()|@*">
        <xsl:copy>
            <xsl:apply-templates select="node()|@*"/>
        </xsl:copy>
    </xsl:template>

    <!-- We do not actually need these and what's more testdefinition DTD
         validation would not pass
    -->
    <xsl:template match="@xml:base"/>

    <!-- Distribute "suite/pre_steps" and "set/pre_steps" among all "case"
         nodes.
         
         This is a workaround for two limitations of the testdefinition DTD:
            (1) the attribute "manual" is not allowed on "set/pre_steps"
            (2) "suite/pre_steps" is not allowed at all.
    -->
    <xsl:template match="suite">
        <xsl:copy>
            <xsl:apply-templates select="node()|@*">
                <xsl:with-param name="suite_pre_steps" select="pre_steps/*"/>
            </xsl:apply-templates>
        </xsl:copy>
    </xsl:template>

    <xsl:template match="suite/pre_steps"/>

    <xsl:template match="set">
        <xsl:param name="suite_pre_steps"/>
        <xsl:copy>
            <xsl:apply-templates select="node()|@*">
                <xsl:with-param name="pre_steps" select="$suite_pre_steps|pre_steps/*"/>
            </xsl:apply-templates>
        </xsl:copy>
    </xsl:template>

    <xsl:template match="set/pre_steps"/>

    <xsl:template match="case">
        <xsl:param name="pre_steps"/>
        <xsl:copy>
            <xsl:apply-templates select="@*"/>
            <xsl:attribute name="manual" select="'true'"/>
            <xsl:copy-of select="$pre_steps"/>
            <xsl:apply-templates select="node()"/>
        </xsl:copy>
    </xsl:template>
</xsl:stylesheet>
